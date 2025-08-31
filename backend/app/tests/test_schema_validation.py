from pathlib import Path
from io import BytesIO

import os
import sys

import pandas as pd
import pytest

# Add project root to path and set minimal env vars
sys.path.append(str(Path(__file__).resolve().parents[3]))
os.environ.setdefault("database_url", "sqlite://")
os.environ.setdefault("jwt_secret_key", "test")
os.environ.setdefault("openai_api_key", "test")
os.environ.setdefault("xero_client_id", "test")
os.environ.setdefault("xero_client_secret", "test")
os.environ.setdefault("xero_redirect_uri", "http://localhost")
os.environ.setdefault("google_client_id", "test")
os.environ.setdefault("google_client_secret", "test")
os.environ.setdefault("google_redirect_uri", "http://localhost")
os.environ.setdefault("secret_key", "test")

from backend.app.ingest.validators import (
    REQUIRED_SHEETS,
    validate_csv_schema,
    validate_excel_schema,
)
from backend.app.ingest.errors import SchemaValidationError


def _build_excel(sheets):
    buf = BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as writer:
        for name, df in sheets.items():
            df.to_excel(writer, sheet_name=name, index=False)
    buf.seek(0)
    return buf.getvalue()


def test_validate_excel_schema_passes_with_valid_template():
    sheets = {}
    for name, cols in REQUIRED_SHEETS.items():
        df = pd.DataFrame(columns=cols)
        sheets[name] = df
    content = _build_excel(sheets)
    # Should not raise
    validate_excel_schema(content)


def test_validate_excel_schema_returns_all_missing_columns():
    sheets = {}
    for name, cols in REQUIRED_SHEETS.items():
        if name == "Activities":
            df_cols = [c for c in cols if c not in {"Activity Name", "Notes"}]
        else:
            df_cols = cols
        sheets[name] = pd.DataFrame(columns=df_cols)
    content = _build_excel(sheets)
    with pytest.raises(SchemaValidationError) as exc:
        validate_excel_schema(content)
    assert exc.value.status_code == 422
    assert exc.value.detail == {
        "sheet": "Activities",
        "missing": ["Activity Name", "Notes"],
    }


def test_validate_csv_schema_case_insensitive_and_missing_columns():
    # Valid when case and whitespace differ
    cols = [c.upper() + " " for c in REQUIRED_SHEETS["Project Info"]]
    df = pd.DataFrame(columns=cols)
    csv_bytes = df.to_csv(index=False).encode("utf-8")
    validate_csv_schema(csv_bytes, "Project Info")

    # Invalid when columns missing
    bad_cols = [c for c in REQUIRED_SHEETS["Outcomes"] if c not in {"Value", "Unit"}]
    df_bad = pd.DataFrame(columns=bad_cols)
    bad_bytes = df_bad.to_csv(index=False).encode("utf-8")
    with pytest.raises(SchemaValidationError) as exc:
        validate_csv_schema(bad_bytes, "Outcomes")
    assert exc.value.status_code == 422
    assert exc.value.detail == {
        "sheet": "Outcomes",
        "missing": ["Value", "Unit"],
    }
