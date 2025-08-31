from io import BytesIO
from pathlib import Path
import os
import sys

import pandas as pd
import pytest

# Configure environment for importing
sys.path.append(str(Path(__file__).resolve().parents[3]))
os.environ.setdefault("database_url", "sqlite://")
os.environ.setdefault("jwt_secret_key", "test")
os.environ.setdefault("secret_key", "test")

from backend.app.ingest.validators import (
    TEMPLATE_SHEETS,
    validate_template_excel,
)


def _build_excel(sheets):
    buf = BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as writer:
        for name, df in sheets.items():
            df.to_excel(writer, sheet_name=name, index=False)
    buf.seek(0)
    return buf.getvalue()


def test_validator_missing_sheet_and_column():
    # Build workbook missing the 'Activities' sheet and a column in 'Project Info'
    sheets = {}
    for name, cols in TEMPLATE_SHEETS.items():
        if name == "Activities":
            continue
        df_cols = list(cols.keys())
        if name == "Project Info":
            df_cols = df_cols[:-1]  # drop last column
        df = pd.DataFrame(columns=df_cols)
        sheets[name] = df
    content = _build_excel(sheets)
    errors = validate_template_excel(content)
    assert {"sheet": "Activities", "column": None, "issue": "missing_sheet"} in errors
    assert {
        "sheet": "Project Info",
        "column": list(TEMPLATE_SHEETS["Project Info"].keys())[-1],
        "issue": "missing_column",
    } in errors


def test_validator_wrong_dtype():
    # Build workbook with incorrect dtype for Beneficiaries.Count (should be int)
    sheets = {}
    for name, cols in TEMPLATE_SHEETS.items():
        df_cols = list(cols.keys())
        df = pd.DataFrame(columns=df_cols)
        if name == "Beneficiaries":
            df = pd.DataFrame(
                {
                    "Project ID": [1],
                    "Date": ["2025-06"],
                    "Beneficiary Group": ["A"],
                    "Count": ["not-int"],
                    "Demographic Info": ["x"],
                    "Location": ["x"],
                    "Notes": ["x"],
                }
            )
        sheets[name] = df
    content = _build_excel(sheets)
    errors = validate_template_excel(content)
    assert {"sheet": "Beneficiaries", "column": "Count", "issue": "invalid_type"} in errors
