from pathlib import Path
import os
import sys
from datetime import date
import uuid

# Setup environment and path
sys.path.append(str(Path(__file__).resolve().parents[3]))
os.environ["database_url"] = "sqlite:///./test.db"
_db_path = Path("test.db")
if _db_path.exists():
    _db_path.unlink()
os.environ.setdefault("jwt_secret_key", "test")
os.environ.setdefault("openai_api_key", "test")
os.environ.setdefault("xero_client_id", "test")
os.environ.setdefault("xero_client_secret", "test")
os.environ.setdefault("xero_redirect_uri", "http://localhost")
os.environ.setdefault("google_client_id", "test")
os.environ.setdefault("google_client_secret", "test")
os.environ.setdefault("google_redirect_uri", "http://localhost")
os.environ.setdefault("secret_key", "test")

from backend.app.database import Base, engine, SessionLocal
from backend.app.models import (
    Project,
    FundingResource,
    Beneficiary,
    Outcome,
    ProjectSummary,
    MonthlyRollup,
    MetricsSummary,
)
from backend.app.metrics.compute import recompute_for_project


def setup_function(_):
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


def test_metrics_compute():
    db = SessionLocal()
    project_id = "p1"
    db.add(
        Project(
            id=project_id,
            owner_org_id="org1",
            project_id="p1",
            name="Project 1",
            source_system="excel",
            schema_version=1,
        )
    )
    db.add(
        FundingResource(
            id=str(uuid.uuid4()),
            project_fk=project_id,
            date=date(2024, 4, 1),
            funding_source="donor",
            received=100.0,
            spent=80.0,
            volunteer_hours=0,
            staff_hours=0,
            source_system="excel",
            schema_version=1,
        )
    )
    db.add(
        Beneficiary(
            id=str(uuid.uuid4()),
            project_fk=project_id,
            date=date(2024, 5, 1),
            group="g1",
            count=20,
            demographic_info="info",
            location="loc",
            notes="b",
            source_system="excel",
            schema_version=1,
        )
    )
    db.add(
        Outcome(
            id=str(uuid.uuid4()),
            project_fk=project_id,
            date=date(2024, 3, 1),
            outcome_metric="metric",
            value=5.0,
            unit="u",
            method="m",
            notes="o",
            source_system="excel",
            schema_version=1,
        )
    )
    db.commit()
    db.close()

    db = SessionLocal()
    recompute_for_project(db, project_id)
    db.close()

    db = SessionLocal()
    ps = db.query(ProjectSummary).filter_by(project_fk=project_id).one()
    assert ps.total_received == 100.0
    assert ps.total_spent == 80.0
    assert ps.total_beneficiaries == 20
    assert ps.cost_per_beneficiary == 4.0

    rollups = {
        r.month: r
        for r in db.query(MonthlyRollup).filter_by(project_fk=project_id).all()
    }
    assert date(2024, 4, 1) in rollups
    assert rollups[date(2024, 4, 1)].total_received == 100.0
    assert rollups[date(2024, 4, 1)].total_spent == 80.0
    assert rollups[date(2024, 4, 1)].total_beneficiaries == 0
    assert rollups[date(2024, 4, 1)].cost_per_beneficiary is None
    assert rollups[date(2024, 4, 1)].source_system == "derived"

    assert date(2024, 5, 1) in rollups
    assert rollups[date(2024, 5, 1)].total_beneficiaries == 20
    assert rollups[date(2024, 5, 1)].total_spent == 0.0
    assert rollups[date(2024, 5, 1)].cost_per_beneficiary == 0.0

    ms = (
        db.query(MetricsSummary)
        .filter_by(project_fk=project_id, metric_name="metric")
        .one()
    )
    assert ms.total_value == 5.0
    db.close()
