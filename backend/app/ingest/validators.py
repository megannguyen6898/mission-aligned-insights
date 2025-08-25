from __future__ import annotations

from io import BytesIO, StringIO
from typing import Dict, Iterable, List, Sequence

import pandas as pd

from .errors import SchemaValidationError

# Required sheets and their corresponding required columns
REQUIRED_SHEETS: Dict[str, Sequence[str]] = {
    "Project Info": [
        "Project ID",
        "Project Name",
        "Org Name",
        "Start Date",
        "End Date",
        "Country",
        "Region",
        "SDG Goal",
        "Notes",
    ],
    "Activities": [
        "Project ID",
        "Date",
        "Activity Type",
        "Activity Name",
        "Beneficiaries Reached",
        "Location",
        "Notes",
    ],
    "Outcomes": [
        "Project ID",
        "Date",
        "Outcome Metric",
        "Value",
        "Unit",
        "Method of Measurement",
        "Notes",
    ],
    "Funding & Resources": [
        "Project ID",
        "Date",
        "Funding Source",
        "Funding Received",
        "Funding Spent",
        "Volunteer Hours",
        "Staff Hours",
        "Notes",
    ],
    "Beneficiaries": [
        "Project ID",
        "Date",
        "Beneficiary Group",
        "Count",
        "Demographic Info",
        "Location",
        "Notes",
    ],
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
