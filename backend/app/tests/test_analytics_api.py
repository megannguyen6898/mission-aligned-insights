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
    os.environ.setdefault("jwt_secret", "test")
    os.environ.setdefault("secret_key", "test")
    os.environ.setdefault("MB_SITE_URL", "http://mb.local")
    os.environ.setdefault("MB_ENCRYPTION_SECRET", "a" * 32)
    from backend.app.database import Base, engine
    Base.metadata.create_all(bind=engine)


def _stage_and_load(batch_id: str):
    from backend.app.database import SessionLocal
    from backend.app.models import (
        ImportBatch,
        StgProjectInfo,
        StgActivity,
        StgBeneficiary,
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
    resp = client.get("/api/analytics/kpis", params={"org_id": "org1", "range": "last_90d"})
    assert resp.status_code == 200
    data = resp.json()
    assert {"projects", "beneficiaries", "spend", "activities"} <= data.keys()

    resp2 = client.get(
        "/api/analytics/series",
        params={
            "metric": "activities_by_month",
            "org_id": "org1",
            "from": "2024-01-01",
            "to": "2024-12-31",
        },
    )
    assert resp2.status_code == 200
    assert isinstance(resp2.json(), list)


def test_metabase_signed():
    from backend.app.main import app
    client = TestClient(app)
    resp = client.post("/api/metabase/signed", json={"resource": "dashboard", "id": 1})
    assert resp.status_code == 200
    assert "url" in resp.json()
