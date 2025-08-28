from __future__ import annotations

from io import BytesIO, StringIO
from typing import Dict, Iterable, List, Sequence

import pandas as pd

from .errors import SchemaValidationError

# ===== Excel template specification =====
# Used by the uploads API and staging pipeline for validating workbook structure.
TEMPLATE_VERSION = "v1"

# Mapping of sheet name to required columns and expected Python types. Only
# numeric columns are type-checked; all others are treated as strings.
TEMPLATE_SHEETS: Dict[str, Dict[str, type]] = {
    "Project Info": {
        "Project ID": str,
        "Project Name": str,
        "Org Name": str,
        "Start Date": str,
        "End Date": str,
        "Country": str,
        "Region": str,
        "SDG Goal": str,
        "Notes": str,
    },
    "Activities": {
        "Project ID": str,
        "Date": str,
        "Activity Type": str,
        "Activity Name": str,
        "Beneficiaries Reached": int,
        "Location": str,
        "Notes": str,
    },
    "Outcomes": {
        "Project ID": str,
        "Date": str,
        "Outcome Metric": str,
        "Value": float,
        "Unit": str,
        "Method of Measurement": str,
        "Notes": str,
    },
    "Funding & Resources": {
        "Project ID": str,
        "Date": str,
        "Funding Source": str,
        "Funding Received": float,
        "Funding Spent": float,
        "Volunteer Hours": float,
        "Staff Hours": float,
        "Notes": str,
    },
    "Beneficiaries": {
        "Project ID": str,
        "Date": str,
        "Beneficiary Group": str,
        "Count": int,
        "Demographic Info": str,
        "Location": str,
        "Notes": str,
    },
}

# Derived mapping used by legacy validators and staging logic.
REQUIRED_SHEETS: Dict[str, Sequence[str]] = {
    sheet: list(cols.keys()) for sheet, cols in TEMPLATE_SHEETS.items()
}


def _normalise(columns: Iterable[str]) -> List[str]:
    """Return lowercase, trimmed representations of column names."""
    return [c.strip().lower() for c in columns]


def _validate_columns(df: pd.DataFrame, sheet: str) -> None:
    required = REQUIRED_SHEETS[sheet]
    present = set(_normalise(df.columns))
    missing = [col for col in required if col.strip().lower() not in present]
    if missing:
        raise SchemaValidationError(sheet=sheet, missing=missing)


def validate_excel_schema(content: bytes) -> None:
    """Validate an Excel workbook against the required schema.

    Raises :class:`SchemaValidationError` if a required sheet or column is
    missing.
    """

    sheets = pd.read_excel(BytesIO(content), sheet_name=None)

    for sheet, columns in REQUIRED_SHEETS.items():
        if sheet not in sheets:
            # Entire sheet missing
            raise SchemaValidationError(sheet=sheet, missing=list(columns))
        _validate_columns(sheets[sheet], sheet)


def validate_csv_schema(content: bytes, sheet: str) -> None:
    """Validate a CSV file against the schema for ``sheet``.

    ``sheet`` must be one of the keys in :data:`REQUIRED_SHEETS`.
    """

    if sheet not in REQUIRED_SHEETS:
        raise ValueError(f"Unknown sheet '{sheet}'")

    df = pd.read_csv(StringIO(content.decode("utf-8")))
    _validate_columns(df, sheet)


def validate_template_excel(content: bytes) -> List[dict]:
    """Validate the Excel template used for bulk data uploads.

    Returns a list of error dictionaries with keys ``sheet``, ``column`` and
    ``issue``. If the list is empty, the workbook conforms to the expected
    schema.
    """

    errors: List[dict] = []
    sheets = pd.read_excel(BytesIO(content), sheet_name=None)

    for sheet, columns in TEMPLATE_SHEETS.items():
        if sheet not in sheets:
            errors.append({"sheet": sheet, "column": None, "issue": "missing_sheet"})
            continue
        df = sheets[sheet]
        for col, expected in columns.items():
            if col not in df.columns:
                errors.append({"sheet": sheet, "column": col, "issue": "missing_column"})
                continue
            series = df[col]
            if expected in (int, float) and not pd.api.types.is_numeric_dtype(series):
                errors.append({"sheet": sheet, "column": col, "issue": "invalid_type"})
    return errors
