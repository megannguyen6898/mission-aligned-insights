from pathlib import Path
import os
import sys
import uuid

import pandas as pd
import pytest

# Setup environment and path
sys.path.append(str(Path(__file__).resolve().parents[3]))
os.environ["database_url"] = "sqlite:///./test.db"
_db_path = Path("test.db")
if _db_path.exists():
    _db_path.unlink()
os.environ.setdefault("jwt_secret", "test")
os.environ.setdefault("openai_api_key", "test")
os.environ.setdefault("xero_client_id", "test")
os.environ.setdefault("xero_client_secret", "test")
os.environ.setdefault("xero_redirect_uri", "http://localhost")
os.environ.setdefault("google_client_id", "test")
os.environ.setdefault("google_client_secret", "test")
os.environ.setdefault("google_redirect_uri", "http://localhost")
os.environ.setdefault("secret_key", "test")

from backend.app.database import Base, engine, SessionLocal
from backend.app.ingest.validators import REQUIRED_SHEETS
from backend.app.ingest.parse_and_stage import parse_and_stage
from backend.app.ingest.errors import SchemaValidationError
from backend.app.models.staging import (
    StgProjectInfo,
    StgActivity,
    StgOutcome,
    StgFundingResource,
    StgBeneficiary,
)

# Ensure tables exist
Base.metadata.create_all(bind=engine)


def _build_workbook(tmp_path: Path) -> Path:
    sheets = {}
    for name, cols in REQUIRED_SHEETS.items():
        rows = [{c: f"{c} value" for c in cols}]
        if name == "Project Info":
            bad = {c: f"{c} value" for c in cols if c != "Project ID"}
            rows.append(bad)
        df = pd.DataFrame(rows)
        sheets[name] = df
    path = tmp_path / "data.xlsx"
    with pd.ExcelWriter(path) as writer:
        for name, df in sheets.items():
            df.to_excel(writer, sheet_name=name, index=False)
    return path


def test_parse_and_stage_excel(tmp_path):
    path = _build_workbook(tmp_path)
    counts = parse_and_stage(
        upload_id=str(uuid.uuid4()),
        import_batch_id=str(uuid.uuid4()),
        file_path=str(path),
    )
    assert counts == {
        "project_info": 2,
        "activities": 1,
        "outcomes": 1,
        "funding_resources": 1,
        "beneficiaries": 1,
    }
    db = SessionLocal()
    row = (
        db.query(StgProjectInfo)
        .filter(StgProjectInfo.row_num == 2)
        .one()
    )
    assert row.parse_errors == {"missing": ["Project ID"]}
    db.close()


def test_parse_and_stage_csv(tmp_path):
    cols = REQUIRED_SHEETS["Project Info"]
    df = pd.DataFrame([{c: "val" for c in cols}])
    path = tmp_path / "project_info.csv"
    df.to_csv(path, index=False)
    counts = parse_and_stage(
        upload_id=str(uuid.uuid4()),
        import_batch_id=str(uuid.uuid4()),
        file_path=str(path),
    )
    assert counts["project_info"] == 1
    db = SessionLocal()
    assert db.query(StgProjectInfo).count() >= 1
    db.close()


def test_parse_and_stage_schema_error(tmp_path):
    sheets = {}
    for name, cols in REQUIRED_SHEETS.items():
        if name == "Activities":
            df = pd.DataFrame(columns=[c for c in cols if c != "Activity Name"])
        else:
            df = pd.DataFrame(columns=cols)
        sheets[name] = df
    path = tmp_path / "bad.xlsx"
    with pd.ExcelWriter(path) as writer:
        for name, df in sheets.items():
            df.to_excel(writer, sheet_name=name, index=False)
    with pytest.raises(SchemaValidationError):
        parse_and_stage(
            upload_id=str(uuid.uuid4()),
            import_batch_id=str(uuid.uuid4()),
            file_path=str(path),
        )
