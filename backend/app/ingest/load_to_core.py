from __future__ import annotations

import uuid
from datetime import date

from sqlalchemy.orm import Session
from sqlalchemy import text

from ..database import SessionLocal
from ..models import (
    Project,
    Activity,
    Outcome,
    FundingResource,
    Beneficiary,
    StgProjectInfo,
    StgActivity,
    StgOutcome,
    StgFundingResource,
    StgBeneficiary,
)


def _parse_date(val: str | None) -> date | None:
    if not val:
        return None
    return date.fromisoformat(val)


def _parse_int(val):
    if val is None or val == "":
        return None
    return int(val)


def _parse_float(val):
    if val is None or val == "":
        return None
    return float(val)


def load_to_core(import_batch_id: str) -> dict:
    """Load normalized data from staging tables into core tables.

    The function performs idempotent upserts based on natural keys or the
    stored row hash.  When the same data is ingested multiple times it
    results in no changes to the core tables.
    """

    session: Session = SessionLocal()
    # Ensure SQLite enforces foreign key constraints
    session.execute(text("PRAGMA foreign_keys=ON"))
    counts = {
        "projects": {"inserted": 0, "updated": 0},
        "activities": {"inserted": 0, "updated": 0},
        "outcomes": {"inserted": 0, "updated": 0},
        "funding_resources": {"inserted": 0, "updated": 0},
        "beneficiaries": {"inserted": 0, "updated": 0},
    }

    try:
        # Projects ---------------------------------------------------------
        project_rows = (
            session.query(StgProjectInfo)
            .filter(
                StgProjectInfo.import_batch_id == import_batch_id,
                StgProjectInfo.parse_errors.is_(None),
            )
            .all()
        )
        for row in project_rows:
            data = row.raw_json
            owner = data.get("owner_org_id")
            pid = data.get("project_id")
            existing = (
                session.query(Project)
                .filter_by(owner_org_id=owner, project_id=pid)
                .one_or_none()
            )
            if existing:
                if existing.row_hash != row.row_hash:
                    existing.name = data.get("name")
                    existing.org_name = data.get("org_name")
                    existing.start_date = _parse_date(data.get("start_date"))
                    existing.end_date = _parse_date(data.get("end_date"))
                    existing.country = data.get("country")
                    existing.region = data.get("region")
                    existing.sdg_goal = data.get("sdg_goal")
                    existing.notes = data.get("notes")
                    existing.row_hash = row.row_hash
                    existing.source_system = row.source_system
                    existing.external_id = row.external_id
                    existing.ingested_at = row.ingested_at
                    existing.import_batch_id = row.import_batch_id
                    existing.schema_version = row.schema_version
                    counts["projects"]["updated"] += 1
            else:
                proj = Project(
                    id=str(uuid.uuid4()),
                    owner_org_id=owner,
                    project_id=pid,
                    name=data.get("name"),
                    org_name=data.get("org_name"),
                    start_date=_parse_date(data.get("start_date")),
                    end_date=_parse_date(data.get("end_date")),
                    country=data.get("country"),
                    region=data.get("region"),
                    sdg_goal=data.get("sdg_goal"),
                    notes=data.get("notes"),
                    row_hash=row.row_hash,
                    source_system=row.source_system,
                    external_id=row.external_id,
                    ingested_at=row.ingested_at,
                    import_batch_id=row.import_batch_id,
                    schema_version=row.schema_version,
                )
                session.add(proj)
                counts["projects"]["inserted"] += 1

        # ensure projects are flushed so children can reference them
        session.flush()

        # Activities ------------------------------------------------------
        activity_rows = (
            session.query(StgActivity)
            .filter(
                StgActivity.import_batch_id == import_batch_id,
                StgActivity.parse_errors.is_(None),
            )
            .all()
        )
        for row in activity_rows:
            data = row.raw_json
            owner = data.get("owner_org_id")
            pid = data.get("project_id")
            project = (
                session.query(Project)
                .filter_by(owner_org_id=owner, project_id=pid)
                .one_or_none()
            )
            project_fk = project.id if project else data.get("project_id")
            existing = session.query(Activity).filter(Activity.row_hash == row.row_hash).one_or_none()
            if not existing:
                existing = (
                    session.query(Activity)
                    .filter(
                        Activity.project_fk == project_fk,
                        Activity.activity_name == data.get("activity_name"),
                        Activity.date == _parse_date(data.get("date")),
                    )
                    .one_or_none()
                )
            if existing:
                if existing.row_hash != row.row_hash:
                    existing.activity_type = data.get("activity_type")
                    existing.beneficiaries_reached = _parse_int(
                        data.get("beneficiaries_reached")
                    )
                    existing.location = data.get("location")
                    existing.notes = data.get("notes")
                    existing.row_hash = row.row_hash
                    existing.source_system = row.source_system
                    existing.external_id = row.external_id
                    existing.ingested_at = row.ingested_at
                    existing.import_batch_id = row.import_batch_id
                    existing.schema_version = row.schema_version
                    counts["activities"]["updated"] += 1
            else:
                obj = Activity(
                    id=str(uuid.uuid4()),
                    project_fk=project_fk,
                    date=_parse_date(data.get("date")),
                    activity_type=data.get("activity_type"),
                    activity_name=data.get("activity_name"),
                    beneficiaries_reached=_parse_int(
                        data.get("beneficiaries_reached")
                    ),
                    location=data.get("location"),
                    notes=data.get("notes"),
                    row_hash=row.row_hash,
                    source_system=row.source_system,
                    external_id=row.external_id,
                    ingested_at=row.ingested_at,
                    import_batch_id=row.import_batch_id,
                    schema_version=row.schema_version,
                )
                session.add(obj)
                counts["activities"]["inserted"] += 1

        # Outcomes --------------------------------------------------------
        outcome_rows = (
            session.query(StgOutcome)
            .filter(
                StgOutcome.import_batch_id == import_batch_id,
                StgOutcome.parse_errors.is_(None),
            )
            .all()
        )
        for row in outcome_rows:
            data = row.raw_json
            owner = data.get("owner_org_id")
            pid = data.get("project_id")
            project = (
                session.query(Project)
                .filter_by(owner_org_id=owner, project_id=pid)
                .one_or_none()
            )
            project_fk = project.id if project else data.get("project_id")
            existing = session.query(Outcome).filter(Outcome.row_hash == row.row_hash).one_or_none()
            if not existing:
                existing = (
                    session.query(Outcome)
                    .filter(
                        Outcome.project_fk == project_fk,
                        Outcome.outcome_metric == data.get("outcome_metric"),
                        Outcome.date == _parse_date(data.get("date")),
                    )
                    .one_or_none()
                )
            if existing:
                if existing.row_hash != row.row_hash:
                    existing.value = _parse_float(data.get("value"))
                    existing.unit = data.get("unit")
                    existing.method = data.get("method")
                    existing.notes = data.get("notes")
                    existing.row_hash = row.row_hash
                    existing.source_system = row.source_system
                    existing.external_id = row.external_id
                    existing.ingested_at = row.ingested_at
                    existing.import_batch_id = row.import_batch_id
                    existing.schema_version = row.schema_version
                    counts["outcomes"]["updated"] += 1
            else:
                obj = Outcome(
                    id=str(uuid.uuid4()),
                    project_fk=project_fk,
                    date=_parse_date(data.get("date")),
                    outcome_metric=data.get("outcome_metric"),
                    value=_parse_float(data.get("value")),
                    unit=data.get("unit"),
                    method=data.get("method"),
                    notes=data.get("notes"),
                    row_hash=row.row_hash,
                    source_system=row.source_system,
                    external_id=row.external_id,
                    ingested_at=row.ingested_at,
                    import_batch_id=row.import_batch_id,
                    schema_version=row.schema_version,
                )
                session.add(obj)
                counts["outcomes"]["inserted"] += 1

        # Funding resources -----------------------------------------------
        fr_rows = (
            session.query(StgFundingResource)
            .filter(
                StgFundingResource.import_batch_id == import_batch_id,
                StgFundingResource.parse_errors.is_(None),
            )
            .all()
        )
        for row in fr_rows:
            data = row.raw_json
            owner = data.get("owner_org_id")
            pid = data.get("project_id")
            project = (
                session.query(Project)
                .filter_by(owner_org_id=owner, project_id=pid)
                .one_or_none()
            )
            project_fk = project.id if project else data.get("project_id")
            existing = session.query(FundingResource).filter(FundingResource.row_hash == row.row_hash).one_or_none()
            if not existing:
                existing = (
                    session.query(FundingResource)
                    .filter(
                        FundingResource.project_fk == project_fk,
                        FundingResource.funding_source == data.get("funding_source"),
                        FundingResource.date == _parse_date(data.get("date")),
                    )
                    .one_or_none()
                )
            if existing:
                if existing.row_hash != row.row_hash:
                    existing.received = _parse_float(data.get("received"))
                    existing.spent = _parse_float(data.get("spent"))
                    existing.volunteer_hours = _parse_float(
                        data.get("volunteer_hours")
                    )
                    existing.staff_hours = _parse_float(data.get("staff_hours"))
                    existing.notes = data.get("notes")
                    existing.row_hash = row.row_hash
                    existing.source_system = row.source_system
                    existing.external_id = row.external_id
                    existing.ingested_at = row.ingested_at
                    existing.import_batch_id = row.import_batch_id
                    existing.schema_version = row.schema_version
                    counts["funding_resources"]["updated"] += 1
            else:
                obj = FundingResource(
                    id=str(uuid.uuid4()),
                    project_fk=project_fk,
                    date=_parse_date(data.get("date")),
                    funding_source=data.get("funding_source"),
                    received=_parse_float(data.get("received")),
                    spent=_parse_float(data.get("spent")),
                    volunteer_hours=_parse_float(data.get("volunteer_hours")),
                    staff_hours=_parse_float(data.get("staff_hours")),
                    notes=data.get("notes"),
                    row_hash=row.row_hash,
                    source_system=row.source_system,
                    external_id=row.external_id,
                    ingested_at=row.ingested_at,
                    import_batch_id=row.import_batch_id,
                    schema_version=row.schema_version,
                )
                session.add(obj)
                counts["funding_resources"]["inserted"] += 1

        # Beneficiaries ---------------------------------------------------
        ben_rows = (
            session.query(StgBeneficiary)
            .filter(
                StgBeneficiary.import_batch_id == import_batch_id,
                StgBeneficiary.parse_errors.is_(None),
            )
            .all()
        )
        for row in ben_rows:
            data = row.raw_json
            owner = data.get("owner_org_id")
            pid = data.get("project_id")
            project = (
                session.query(Project)
                .filter_by(owner_org_id=owner, project_id=pid)
                .one_or_none()
            )
            project_fk = project.id if project else data.get("project_id")
            existing = session.query(Beneficiary).filter(Beneficiary.row_hash == row.row_hash).one_or_none()
            if not existing:
                existing = (
                    session.query(Beneficiary)
                    .filter(
                        Beneficiary.project_fk == project_fk,
                        Beneficiary.group == data.get("group"),
                        Beneficiary.date == _parse_date(data.get("date")),
                    )
                    .one_or_none()
                )
            if existing:
                if existing.row_hash != row.row_hash:
                    existing.count = _parse_int(data.get("count"))
                    existing.demographic_info = data.get("demographic_info")
                    existing.location = data.get("location")
                    existing.notes = data.get("notes")
                    existing.row_hash = row.row_hash
                    existing.source_system = row.source_system
                    existing.external_id = row.external_id
                    existing.ingested_at = row.ingested_at
                    existing.import_batch_id = row.import_batch_id
                    existing.schema_version = row.schema_version
                    counts["beneficiaries"]["updated"] += 1
            else:
                obj = Beneficiary(
                    id=str(uuid.uuid4()),
                    project_fk=project_fk,
                    date=_parse_date(data.get("date")),
                    group=data.get("group"),
                    count=_parse_int(data.get("count")),
                    demographic_info=data.get("demographic_info"),
                    location=data.get("location"),
                    notes=data.get("notes"),
                    row_hash=row.row_hash,
                    source_system=row.source_system,
                    external_id=row.external_id,
                    ingested_at=row.ingested_at,
                    import_batch_id=row.import_batch_id,
                    schema_version=row.schema_version,
                )
                session.add(obj)
                counts["beneficiaries"]["inserted"] += 1

        session.commit()
        return counts
    finally:
        session.close()

