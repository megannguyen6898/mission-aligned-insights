import os
import sys
import uuid
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

sys.path.append(str(Path(__file__).resolve().parents[3]))


def setup_function(_):
    db_path = Path("analytics_test.db")
    if db_path.exists():
        db_path.unlink()
    os.environ["database_url"] = "sqlite:///./analytics_test.db"
    os.environ.setdefault("jwt_secret_key", "test")
    os.environ.setdefault("secret_key", "test")
    from backend.app.database import Base, engine
    Base.metadata.create_all(bind=engine)


def _stage_and_load(batch_id: str):
    from backend.app.database import SessionLocal
    from backend.app.models import (
        ImportBatch,
        StgProjectInfo,
        StgActivity,
        StgBeneficiary,
        StgFundingResource,
        StgOutcome,
    )
    from backend.app.ingest.hash import canonical_row_hash
    from backend.app.ingest.load_to_core import load_to_core
    from backend.app.services.analytics_service import AnalyticsService

    db = SessionLocal()
    db.add(
        ImportBatch(
            id=batch_id,
            source_system="excel",
            schema_version=1,
            triggered_by_user_id="user",
        )
    )
    proj_data = {"owner_org_id": "org1", "project_id": "p1"}
    db.add(
        StgProjectInfo(
            id=str(uuid.uuid4()),
            upload_id="u1",
            row_num=1,
            raw_json=proj_data,
            row_hash=canonical_row_hash(proj_data),
            import_batch_id=batch_id,
        )
    )
    act_data = {
        "owner_org_id": "org1",
        "project_id": "p1",
        "date": "2024-01-15",
        "activity_name": "A1",
    }
    db.add(
        StgActivity(
            id=str(uuid.uuid4()),
            upload_id="u1",
            row_num=1,
            raw_json=act_data,
            row_hash=canonical_row_hash(act_data),
            import_batch_id=batch_id,
        )
    )
    ben_data = {
        "owner_org_id": "org1",
        "project_id": "p1",
        "date": "2024-01-15",
        "group": "g1",
        "count": 5,
    }
    db.add(
        StgBeneficiary(
            id=str(uuid.uuid4()),
            upload_id="u1",
            row_num=1,
            raw_json=ben_data,
            row_hash=canonical_row_hash(ben_data),
            import_batch_id=batch_id,
        )
    )

    fund_data = {
        "owner_org_id": "org1",
        "project_id": "p1",
        "date": "2024-01-15",
        "funding_source": "Stipends",
        "spent": 1200,
        "volunteer_hours": 40,
    }
    db.add(
        StgFundingResource(
            id=str(uuid.uuid4()),
            upload_id="u1",
            row_num=1,
            raw_json=fund_data,
            row_hash=canonical_row_hash(fund_data),
            import_batch_id=batch_id,
        )
    )

    outcome_data = {
        "owner_org_id": "org1",
        "project_id": "p1",
        "date": "2024-01-15",
        "outcome_metric": "Satisfaction Score",
        "value": 4.2,
        "unit": "score",
    }
    db.add(
        StgOutcome(
            id=str(uuid.uuid4()),
            upload_id="u1",
            row_num=1,
            raw_json=outcome_data,
            row_hash=canonical_row_hash(outcome_data),
            import_batch_id=batch_id,
        )
    )
    db.commit()
    db.close()
    load_to_core(batch_id)
    db = SessionLocal()
    AnalyticsService().refresh_facts(db)
    db.close()


def test_facts_idempotent():
    from backend.app.database import SessionLocal
    from backend.app.services.analytics_service import AnalyticsService
    from backend.app.models import ActivityOutcomeFact

    batch = str(uuid.uuid4())
    _stage_and_load(batch)
    db = SessionLocal()
    svc = AnalyticsService()
    count1 = db.query(ActivityOutcomeFact).count()
    svc.refresh_facts(db)
    count2 = db.query(ActivityOutcomeFact).count()
    db.close()
    assert count1 == count2


def test_analytics_endpoints():
    batch = str(uuid.uuid4())
    _stage_and_load(batch)
    from backend.app.main import app

    client = TestClient(app)

    resp = client.get("/api/analytics/kpis", params={"space_id": "org1"})
    assert resp.status_code == 200
    payload = resp.json()
    assert "kpis" in payload
    assert len(payload["kpis"]) >= 3
    first = payload["kpis"][0]
    assert {"label", "value", "delta", "unit"} <= first.keys()

    resp_series = client.get(
        "/api/analytics/series",
        params={
            "space_id": "org1",
            "metric": "beneficiaries,completions",
            "group_by": "year",
            "time_range": "2023..2024",
        },
    )
    assert resp_series.status_code == 200
    series_payload = resp_series.json()
    assert "series" in series_payload
    assert isinstance(series_payload["series"], list)
    assert series_payload["series"]
    assert "points" in series_payload["series"][0]

    resp_region = client.get(
        "/api/analytics/series",
        params={
            "space_id": "org1",
            "metric": "spend",
            "group_by": "region",
        },
    )
    assert resp_region.status_code == 200
    region_payload = resp_region.json()
    assert region_payload["series"][0]["points"]


def test_analytics_bad_requests():
    from backend.app.main import app

    client = TestClient(app)

    bad_metric = client.get(
        "/api/analytics/series",
        params={"space_id": "org1", "metric": "made_up"},
    )
    assert bad_metric.status_code == 400

    bad_range = client.get(
        "/api/analytics/series",
        params={
            "space_id": "org1",
            "metric": "beneficiaries",
            "time_range": "not-a-range",
        },
    )
    assert bad_range.status_code == 400
