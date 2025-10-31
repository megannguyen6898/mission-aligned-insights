from __future__ import annotations

from dataclasses import dataclass
from io import BytesIO
from typing import Any, Dict, List, Optional

import pandas as pd
from pandas.api.types import is_datetime64_any_dtype, is_numeric_dtype


@dataclass
class ValidationResult:
    dataframe: pd.DataFrame
    schema: List[Dict[str, Any]]
    preview: List[Dict[str, Any]]
    row_count: int
    numeric_columns: List[str]
    categorical_columns: List[str]
    datetime_columns: List[str]


def _detect_semantic_type(series: pd.Series) -> str:
    if is_datetime64_any_dtype(series):
        return "datetime"
    if is_numeric_dtype(series):
        return "numeric"
    if series.dropna().astype(str).str.len().mean() > 40:
        return "text"
    return "categorical"


def _infer_schema(df: pd.DataFrame) -> List[Dict[str, Any]]:
    schema: List[Dict[str, Any]] = []
    for column in df.columns:
        series = df[column]
        semantic_type = _detect_semantic_type(series)
        missing_ratio = float(series.isna().mean())
        sample_values = series.dropna().astype(str).head(5).tolist()
        schema.append(
            {
                "name": str(column),
                "dtype": str(series.dtype),
                "semantic_type": semantic_type,
                "missing_ratio": round(missing_ratio, 4),
                "sample_values": sample_values,
            }
        )
    return schema


def _preview_rows(df: pd.DataFrame, limit: int = 20) -> List[Dict[str, Any]]:
    preview_df = df.head(limit).fillna("")
    return preview_df.to_dict(orient="records")


def analyse_workbook(raw_bytes: bytes, worksheet: Optional[str] = None) -> ValidationResult:
    df = pd.read_excel(BytesIO(raw_bytes), sheet_name=worksheet)
    if df.empty:
        raise ValueError("The uploaded workbook contains no rows.")

    schema = _infer_schema(df)
    preview = _preview_rows(df)
    numeric_columns = [col["name"] for col in schema if col["semantic_type"] == "numeric"]
    categorical_columns = [col["name"] for col in schema if col["semantic_type"] == "categorical"]
    datetime_columns = [col["name"] for col in schema if col["semantic_type"] == "datetime"]

    return ValidationResult(
        dataframe=df,
        schema=schema,
        preview=preview,
        row_count=int(df.shape[0]),
        numeric_columns=numeric_columns,
        categorical_columns=categorical_columns,
        datetime_columns=datetime_columns,
    )
