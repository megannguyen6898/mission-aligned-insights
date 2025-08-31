from pathlib import Path
import os
import sys
import uuid

import pytest
from sqlalchemy.exc import IntegrityError

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
from backend.app.ingest.hash import canonical_row_hash
from backend.app.ingest.load_to_core import load_to_core
from backend.app.models import (
    ImportBatch,
    StgProjectInfo,
    StgActivity,
    StgOutcome,
    StgFundingResource,
    StgBeneficiary,
    Project,
    Activity,
    Outcome,
    FundingResource,
    Beneficiary,
)


def setup_function(_):
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


def _add_import_batch(db, batch_id: str):
    db.add(
        ImportBatch(
            id=batch_id,
            source_system="excel",
            schema_version=1,
            triggered_by_user_id="user",
        )
    )


def _stage_sample_data(batch_id: str):
    db = SessionLocal()
    _add_import_batch(db, batch_id)

    project_data = {
        "owner_org_id": "org1",
        "project_id": "p1",
        "name": "Project 1",
        "org_name": "Org 1",
        "start_date": "2024-01-01",
        "end_date": "2024-12-31",
        "country": "X",
        "region": "Y",
        "sdg_goal": "goal",
        "notes": "n",
    }
    proj = StgProjectInfo(
        id=str(uuid.uuid4()),
        upload_id="u1",
        row_num=1,
        raw_json=project_data,
        row_hash=canonical_row_hash(project_data),
        import_batch_id=batch_id,
        source_system="excel",
        schema_version=1,
    )
    db.add(proj)

    activity_data = {
        "owner_org_id": "org1",
        "project_id": "p1",
        "date": "2024-02-01",
        "activity_type": "type",
        "activity_name": "act",
        "beneficiaries_reached": 10,
        "location": "loc",
        "notes": "a",
    }
    db.add(
        StgActivity(
            id=str(uuid.uuid4()),
            upload_id="u1",
            row_num=1,
            raw_json=activity_data,
            row_hash=canonical_row_hash(activity_data),
            import_batch_id=batch_id,
            source_system="excel",
            schema_version=1,
        )
    )

    outcome_data = {
        "owner_org_id": "org1",
        "project_id": "p1",
        "date": "2024-03-01",
        "outcome_metric": "metric",
        "value": 5,
        "unit": "u",
        "method": "m",
        "notes": "o",
    }
    db.add(
        StgOutcome(
            id=str(uuid.uuid4()),
            upload_id="u1",
            row_num=1,
            raw_json=outcome_data,
            row_hash=canonical_row_hash(outcome_data),
            import_batch_id=batch_id,
            source_system="excel",
            schema_version=1,
        )
    )

    fr_data = {
        "owner_org_id": "org1",
        "project_id": "p1",
        "date": "2024-04-01",
        "funding_source": "donor",
        "received": 100.0,
        "spent": 80.0,
        "volunteer_hours": 5,
        "staff_hours": 3,
        "notes": "f",
    }
    db.add(
        StgFundingResource(
            id=str(uuid.uuid4()),
            upload_id="u1",
            row_num=1,
            raw_json=fr_data,
            row_hash=canonical_row_hash(fr_data),
            import_batch_id=batch_id,
            source_system="excel",
            schema_version=1,
        )
    )

    ben_data = {
        "owner_org_id": "org1",
        "project_id": "p1",
        "date": "2024-05-01",
        "group": "g1",
        "count": 20,
        "demographic_info": "info",
        "location": "loc",
        "notes": "b",
    }
    db.add(
        StgBeneficiary(
            id=str(uuid.uuid4()),
            upload_id="u1",
            row_num=1,
            raw_json=ben_data,
            row_hash=canonical_row_hash(ben_data),
            import_batch_id=batch_id,
            source_system="excel",
            schema_version=1,
        )
    )

    db.commit()
    db.close()


def test_load_to_core_idempotent():
    batch_id = str(uuid.uuid4())
    _stage_sample_data(batch_id)

    counts1 = load_to_core(batch_id)
    assert counts1 == {
        "projects": {"inserted": 1, "updated": 0},
        "activities": {"inserted": 1, "updated": 0},
        "outcomes": {"inserted": 1, "updated": 0},
        "funding_resources": {"inserted": 1, "updated": 0},
        "beneficiaries": {"inserted": 1, "updated": 0},
    }

    db = SessionLocal()
    assert db.query(Project).count() == 1
    assert db.query(Activity).count() == 1
    assert db.query(Outcome).count() == 1
    assert db.query(FundingResource).count() == 1
    assert db.query(Beneficiary).count() == 1
    db.close()

    counts2 = load_to_core(batch_id)
    assert counts2 == {
        "projects": {"inserted": 0, "updated": 0},
        "activities": {"inserted": 0, "updated": 0},
        "outcomes": {"inserted": 0, "updated": 0},
        "funding_resources": {"inserted": 0, "updated": 0},
        "beneficiaries": {"inserted": 0, "updated": 0},
    }


def test_load_to_core_fk_enforced():
    batch_id = str(uuid.uuid4())
    db = SessionLocal()
    _add_import_batch(db, batch_id)
    bad_activity = {
        "owner_org_id": "org1",
        "project_id": "missing",
        "date": "2024-01-01",
        "activity_type": "t",
        "activity_name": "a",
    }
    db.add(
        StgActivity(
            id=str(uuid.uuid4()),
            upload_id="u1",
            row_num=1,
            raw_json=bad_activity,
            row_hash=canonical_row_hash(bad_activity),
            import_batch_id=batch_id,
            source_system="excel",
            schema_version=1,
        )
    )
    db.commit()
    db.close()

    with pytest.raises(IntegrityError):
        load_to_core(batch_id)

