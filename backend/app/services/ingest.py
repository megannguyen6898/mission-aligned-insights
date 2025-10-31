from __future__ import annotations

from typing import Optional

import pandas as pd
from sqlalchemy import text

from ..database import engine


def write_dataframe(df: pd.DataFrame, table_name: str, if_exists: str = "replace") -> None:
    df.to_sql(table_name, engine, if_exists=if_exists, index=False)


def table_exists(table_name: str) -> bool:
    with engine.connect() as conn:
        result = conn.execute(
            text(
                "SELECT to_regclass(:table_name)"
            ),
            {"table_name": table_name},
        )
        value: Optional[str] = result.scalar()
    return value is not None
