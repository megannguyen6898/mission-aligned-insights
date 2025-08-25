from collections import defaultdict

from sqlalchemy.orm import Session

from ..models import (
    Beneficiary,
    FundingResource,
    Outcome,
    ProjectSummary,
    MonthlyRollup,
    MetricsSummary,
)


def recompute_for_project(db: Session, project_fk: str) -> None:
    """Recompute summary tables for a given project.

    Existing summary data for the project is removed before new values are
    calculated. The function commits the session when finished.
    """

    # Clear existing summaries
    db.query(ProjectSummary).filter_by(project_fk=project_fk).delete()
    db.query(MonthlyRollup).filter_by(project_fk=project_fk).delete()
    db.query(MetricsSummary).filter_by(project_fk=project_fk).delete()
    db.flush()

    # Project level totals
    total_received = (
        db.query(FundingResource)
        .filter_by(project_fk=project_fk)
        .with_entities(FundingResource.received)
    )
    total_received = sum(fr.received or 0 for fr in total_received)

    total_spent = (
        db.query(FundingResource)
        .filter_by(project_fk=project_fk)
        .with_entities(FundingResource.spent)
    )
    total_spent = sum(fr.spent or 0 for fr in total_spent)

    total_beneficiaries = (
        db.query(Beneficiary)
        .filter_by(project_fk=project_fk)
        .with_entities(Beneficiary.count)
    )
    total_beneficiaries = sum(b.count or 0 for b in total_beneficiaries)

    cost_per_beneficiary = (
        total_spent / total_beneficiaries if total_beneficiaries else None
    )

    db.add(
        ProjectSummary(
            project_fk=project_fk,
            total_received=total_received,
            total_spent=total_spent,
            total_beneficiaries=total_beneficiaries,
            cost_per_beneficiary=cost_per_beneficiary,
        )
    )

    # Monthly rollups
    monthly = defaultdict(lambda: {"received": 0.0, "spent": 0.0, "beneficiaries": 0})

    for fr in db.query(FundingResource).filter_by(project_fk=project_fk):
        if fr.date is None:
            continue
        month = fr.date.replace(day=1)
        monthly[month]["received"] += fr.received or 0
        monthly[month]["spent"] += fr.spent or 0

    for ben in db.query(Beneficiary).filter_by(project_fk=project_fk):
        if ben.date is None:
            continue
        month = ben.date.replace(day=1)
        monthly[month]["beneficiaries"] += ben.count or 0

    for month, vals in monthly.items():
        cost = (
            vals["spent"] / vals["beneficiaries"]
            if vals["beneficiaries"]
            else None
        )
        db.add(
            MonthlyRollup(
                project_fk=project_fk,
                month=month,
                total_received=vals["received"],
                total_spent=vals["spent"],
                total_beneficiaries=vals["beneficiaries"],
                cost_per_beneficiary=cost,
                source_system="derived",
            )
        )

    # Metrics summary from outcomes
    q = (
        db.query(Outcome.outcome_metric, Outcome.value)
        .filter(Outcome.project_fk == project_fk)
    )
    metrics = defaultdict(float)
    for metric_name, value in q:
        metrics[metric_name] += value or 0

    for metric_name, total in metrics.items():
        db.add(
            MetricsSummary(
                project_fk=project_fk,
                metric_name=metric_name,
                total_value=total,
            )
        )

    db.commit()
