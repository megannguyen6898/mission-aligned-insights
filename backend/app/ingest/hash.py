import datetime
import hashlib
import json
import math
from typing import Any, Dict


def canonicalize(value: Any) -> Any:
    """Recursively normalize values for stable hashing.

    - Dict keys are sorted.
    - Strings are trimmed and lower-cased.
    - ISO formatted dates are normalized.
    - NaN floats are converted to ``None``.
    """

    if isinstance(value, dict):
        return {k: canonicalize(v) for k, v in sorted(value.items(), key=lambda kv: kv[0])}
    if isinstance(value, list):
        return [canonicalize(v) for v in value]
    if isinstance(value, str):
        v = value.strip().lower()
        candidate = v[:-1] if v.endswith("z") else v
        for parser in (datetime.datetime.fromisoformat, datetime.date.fromisoformat):
            try:
                return parser(candidate).isoformat()
            except ValueError:
                continue
        return v
    if isinstance(value, float) and math.isnan(value):
        return None
    if isinstance(value, (datetime.datetime, datetime.date)):
        return value.isoformat()
    return value


def canonical_row_hash(row: Dict[str, Any]) -> str:
    """Return a deterministic SHA256 hash for a row of data."""

    payload = json.dumps(canonicalize(row), separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()

