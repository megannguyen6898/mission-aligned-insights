from __future__ import annotations

from datetime import datetime, date
from typing import Any, Dict, Iterable, List, Optional, Tuple

import os
import re
from dateutil.relativedelta import relativedelta

from .mapping_loader import load_mapping

PII_REDACTION_ENABLED = os.getenv("PII_REDACTION_ENABLED", "false").lower() == "true"

EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
PHONE_RE = re.compile(r"\+?\d[\d\s().-]{7,}\d")


def _redact_pii(value: Any) -> Any:
    if not isinstance(value, str):
        return value
    value = EMAIL_RE.sub("[REDACTED]", value)
    value = PHONE_RE.sub("[REDACTED]", value)
    return value


DATE_FIELDS = {"date", "start_date", "end_date"}
NUMERIC_FIELDS = {
    "beneficiaries_reached",
    "received",
    "spent",
    "value",
    "volunteer_hours",
    "staff_hours",
    "count",
}
INT_FIELDS = {"beneficiaries_reached", "count"}
CATEGORY_FIELDS = {
    "activity_type",
    "funding_source",
    "group",
    "country",
    "region",
    "sdg_goal",
    "location",
    "unit",
    "method",
}


def coerce_date(s: Any) -> Optional[date]:
    if s in (None, ""):
        return None
    s = str(s).strip()
    # YYYY-MM-DD
    try:
        return datetime.strptime(s, "%Y-%m-%d").date()
    except Exception:
        pass
    # YYYY-MM
    try:
        d = datetime.strptime(s, "%Y-%m")
        # last day of month
        next_month = d.replace(day=28) + relativedelta(days=4)
        last_day = next_month - relativedelta(days=next_month.day)
        return last_day.date()
    except Exception:
        return None


def coerce_number(x: Any) -> Optional[float]:
    try:
        if x in (None, ""):
            return None
        return float(str(x).replace(",", ""))
    except Exception:
        return None


def _standardize_category(value: Any) -> Optional[str]:
    if value in (None, ""):
        return None
    return str(value).strip().title()


def normalize_row(
    raw: Dict[str, Any],
    sheet: str,
    *,
    mapping: Optional[Dict[str, Dict[str, str]]] = None,
) -> Tuple[Dict[str, Any], Optional[Dict[str, List[str]]]]:
    """Normalize a single raw row.

    Parameters
    ----------
    raw: Dict[str, Any]
        Raw row with original column names.
    sheet: str
        Sheet name (e.g., "activities").
    mapping: Optional[Dict[str, Dict[str, str]]]
        Pre-loaded mapping. If not provided it will be loaded for the default
        source system.

    Returns
    -------
    Tuple[Dict[str, Any], Optional[Dict[str, List[str]]]]
        Normalized values dictionary and parse error information.
    """

    if mapping is None:
        mapping = load_mapping()
    sheet_map = mapping.get(sheet.strip().lower(), {})

    normalized: Dict[str, Any] = {}
    invalid_fields: List[str] = []

    for src_key, value in raw.items():
        norm_key = sheet_map.get(str(src_key).strip().lower())
        if norm_key is None:
            continue
        if value in (None, ""):
            normalized[norm_key] = None
            continue
        if norm_key in DATE_FIELDS:
            coerced = coerce_date(value)
            if coerced is None:
                invalid_fields.append(norm_key)
            normalized_value = coerced
        elif norm_key in NUMERIC_FIELDS:
            num = coerce_number(value)
            if num is None:
                invalid_fields.append(norm_key)
            else:
                if norm_key in INT_FIELDS:
                    num = int(num)
            normalized_value = num
        elif norm_key in CATEGORY_FIELDS:
            normalized_value = _standardize_category(value)
        else:
            normalized_value = value

        if PII_REDACTION_ENABLED:
            normalized_value = _redact_pii(normalized_value)
        normalized[norm_key] = normalized_value

    parse_errors = {"invalid": invalid_fields} if invalid_fields else None
    return normalized, parse_errors


def normalize_rows(
    rows: Iterable[Dict[str, Any]],
    sheet: str,
    *,
    mapping: Optional[Dict[str, Dict[str, str]]] = None,
) -> List[Tuple[Dict[str, Any], Optional[Dict[str, List[str]]]]]:
    """Normalize multiple rows for a given sheet."""

    results: List[Tuple[Dict[str, Any], Optional[Dict[str, List[str]]]]] = []
    for row in rows:
        results.append(normalize_row(row, sheet, mapping=mapping))
    return results

