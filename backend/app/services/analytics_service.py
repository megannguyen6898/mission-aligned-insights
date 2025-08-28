from __future__ import annotations

import uuid
from datetime import date
from typing import Any, Dict, List

from sqlalchemy import func
from sqlalchemy.orm import Session

from ..models import (
    Activity,
    Beneficiary,
    FundingResource,
    Project,
    ActivityOutcomeFact,
)


class AnalyticsService:
    """Service for refreshing and querying analytics facts."""

    def refresh_facts(self, db: Session) -> None:
        db.query(ActivityOutcomeFact).delete()
        db.commit()

        rows = (
            db.query(
                Activity.project_fk.label("project_fk"),
                Activity.date.label("activity_date"),
                func.count(Activity.id).label("activities"),
                func.coalesce(func.sum(Beneficiary.count), 0).label("beneficiaries"),
                func.coalesce(func.sum(FundingResource.spent), 0).label("spend"),
            )
            .outerjoin(
                Beneficiary,
                (Beneficiary.project_fk == Activity.project_fk)
                & (Beneficiary.date == Activity.date),
            )
            .outerjoin(
                FundingResource,
                (FundingResource.project_fk == Activity.project_fk)
                & (FundingResource.date == Activity.date),
            )
            .group_by(Activity.project_fk, Activity.date)
        ).all()

        for r in rows:
            db.add(
                ActivityOutcomeFact(
                    id=str(uuid.uuid4()),
                    project_fk=r.project_fk,
                    activity_date=r.activity_date,
                    activities=r.activities or 0,
                    beneficiaries=int(r.beneficiaries or 0),
                    spend=float(r.spend or 0.0),
                )
            )
        db.commit()

    # KPI values
    def kpis(self, db: Session, org_id: str, start: date | None = None) -> Dict[str, Any]:
        q = (
            db.query(
                func.count(func.distinct(ActivityOutcomeFact.project_fk)).label("projects"),
                func.coalesce(func.sum(ActivityOutcomeFact.beneficiaries), 0).label("beneficiaries"),
                func.coalesce(func.sum(ActivityOutcomeFact.spend), 0).label("spend"),
                func.coalesce(func.sum(ActivityOutcomeFact.activities), 0).label("activities"),
            )
            .join(Project, Project.id == ActivityOutcomeFact.project_fk)
            .filter(Project.owner_org_id == org_id)
        )
        if start is not None:
            q = q.filter(ActivityOutcomeFact.activity_date >= start)
        res = q.one()
        return {
            "projects": int(res.projects or 0),
            "beneficiaries": int(res.beneficiaries or 0),
            "spend": float(res.spend or 0.0),
            "activities": int(res.activities or 0),
        }

    def activity_series(self, db: Session, org_id: str, start: date, end: date) -> List[Dict[str, Any]]:
        dialect = db.bind.dialect.name  # type: ignore[attr-defined]
        if dialect == "sqlite":
            month_expr = func.strftime("%Y-%m-01", ActivityOutcomeFact.activity_date)
        else:
            month_expr = func.date_trunc("month", ActivityOutcomeFact.activity_date)

        q = (
            db.query(
                month_expr.label("month"),
                func.sum(ActivityOutcomeFact.activities).label("value"),
            )
            .join(Project, Project.id == ActivityOutcomeFact.project_fk)
            .filter(Project.owner_org_id == org_id)
            .filter(ActivityOutcomeFact.activity_date >= start)
            .filter(ActivityOutcomeFact.activity_date <= end)
            .group_by(month_expr)
            .order_by(month_expr)
        )
        results = []
        for r in q.all():
            if isinstance(r.month, str):
                month = r.month
            else:
                month = r.month.date().isoformat()  # type: ignore[call-arg]
            results.append({"month": month, "value": int(r.value or 0)})
        return results
