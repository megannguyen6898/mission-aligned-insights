import hashlib
import json
import math
from typing import Any, Dict


def canonical_row_hash(row: Dict[str, Any]) -> str:
    """Return a stable hash for a row of data."""
    cleaned: Dict[str, Any] = {}
    for key, value in row.items():
        if isinstance(value, float) and math.isnan(value):
            cleaned[key] = None
        else:
            cleaned[key] = value
    encoded = json.dumps(cleaned, sort_keys=True, default=str)
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()
