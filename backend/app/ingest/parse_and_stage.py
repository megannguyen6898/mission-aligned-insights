from __future__ import annotations

import uuid
from pathlib import Path
from typing import Dict, Any

import pandas as pd
import sqlalchemy as sa

from ..database import SessionLocal, engine
from .validators import (
    REQUIRED_SHEETS,
    validate_excel_schema,
    validate_csv_schema,
)
from .hash import canonical_row_hash

SHEET_TABLE_MAP = {
    "Project Info": "stg_project_info",
    "Activities": "stg_activities",
    "Outcomes": "stg_outcomes",
    "Funding & Resources": "stg_funding_resources",
    "Beneficiaries": "stg_beneficiaries",
}

SHEET_KEY_MAP = {
    "Project Info": "project_info",
    "Activities": "activities",
    "Outcomes": "outcomes",
    "Funding & Resources": "funding_resources",
    "Beneficiaries": "beneficiaries",
}

FILE_SHEET_MAP = {
    "project_info": "Project Info",
    "activities": "Activities",
    "outcomes": "Outcomes",
    "funding_resources": "Funding & Resources",
    "beneficiaries": "Beneficiaries",
}


def _read_workbook(path: Path) -> Dict[str, pd.DataFrame]:
    if path.suffix.lower() == ".csv":
        sheet = FILE_SHEET_MAP.get(path.stem.lower())
        if sheet is None:
            raise ValueError("Unrecognised CSV filename")
        df = pd.read_csv(path)
        return {sheet: df}
    else:
        return pd.read_excel(path, sheet_name=None)


def parse_and_stage(
    *,
    upload_id: str,
    import_batch_id: str,
    file_path: str,
    source_system: str = "excel",
) -> Dict[str, int]:
    path = Path(file_path)
    content = path.read_bytes()
    if path.suffix.lower() == ".csv":
        sheet = FILE_SHEET_MAP.get(path.stem.lower())
        if sheet is None:
            raise ValueError("Unrecognised CSV filename")
        validate_csv_schema(content, sheet)
    else:
        validate_excel_schema(content)

    dfs = _read_workbook(path)
    metadata = sa.MetaData()
    counts = {key: 0 for key in SHEET_KEY_MAP.values()}

    db = SessionLocal()
    try:
        for sheet_name, df in dfs.items():
            table_name = SHEET_TABLE_MAP.get(sheet_name)
            key = SHEET_KEY_MAP.get(sheet_name)
            if table_name is None or key is None:
                continue
            table = sa.Table(table_name, metadata, autoload_with=engine)
            required_cols = REQUIRED_SHEETS[sheet_name]
            for idx, row in df.iterrows():
                raw: Dict[str, Any] = {
                    col: (None if pd.isna(val) else val) for col, val in row.items()
                }
                missing = [c for c in required_cols if pd.isna(row.get(c))]
                parse_errors = {"missing": missing} if missing else None
                stmt = table.insert().values(
                    id=str(uuid.uuid4()),
                    upload_id=upload_id,
                    row_num=int(idx) + 1,
                    raw_json=raw,
                    parse_errors=parse_errors,
                    source_system=source_system,
                    external_id=None,
                    row_hash=canonical_row_hash(raw),
                    import_batch_id=import_batch_id,
                )
                db.execute(stmt)
                counts[key] += 1
        db.commit()
    finally:
        db.close()

    return counts
