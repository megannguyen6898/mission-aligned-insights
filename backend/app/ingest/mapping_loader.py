import yaml
from pathlib import Path
from typing import Dict


def load_mapping(source_system: str = "excel", version: int = 1) -> Dict[str, Dict[str, str]]:
    """Load field mapping configuration.

    Parameters
    ----------
    source_system: str
        Source system identifier (e.g., "excel").
    version: int
        Mapping version number.

    Returns
    -------
    dict
        Nested dictionary mapping sheet names to field mappings where
        each field mapping maps normalized source column names to
        universal schema names.
    """
    mappings_dir = Path(__file__).with_name("mappings")
    path = mappings_dir / f"{source_system}_v{version}.yml"
    with path.open("r", encoding="utf-8") as f:
        raw = yaml.safe_load(f) or {}

    result: Dict[str, Dict[str, str]] = {}
    for sheet_name, fields in raw.items():
        normalized_sheet = sheet_name.strip().lower()
        result[normalized_sheet] = {}
        if not isinstance(fields, dict):
            continue
        for target, source in fields.items():
            if source is None:
                continue
            normalized_source = str(source).strip().lower()
            normalized_target = str(target).strip().lower()
            result[normalized_sheet][normalized_source] = normalized_target
    return result
