from __future__ import annotations

from typing import Dict, List, Tuple

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from ..database import engine
from ..models import Dataset
from .ingest import table_exists


def load_dataset_frame(dataset: Dataset, limit: int = 5000) -> pd.DataFrame:
    if dataset.table_name and table_exists(dataset.table_name):
        query = f'SELECT * FROM "{dataset.table_name}" LIMIT {limit}'
        with engine.connect() as conn:
            df = pd.read_sql_query(query, conn)
            return df
    if dataset.preview:
        return pd.DataFrame(dataset.preview)
    return pd.DataFrame()


def _coerce_datetime(df: pd.DataFrame, columns: List[str]) -> pd.DataFrame:
    for column in columns:
        if column in df:
            df[column] = pd.to_datetime(df[column], errors="coerce")
    return df


def _numeric_summary(df: pd.DataFrame, numeric_columns: List[str]) -> Tuple[List[str], List[str], List[str]]:
    labels: List[str] = []
    totals: List[str] = []
    averages: List[str] = []
    for column in numeric_columns:
        series = pd.to_numeric(df[column], errors="coerce")
        total = float(series.sum())
        mean = float(series.mean()) if not series.empty else 0.0
        labels.append(column)
        totals.append(f"{total:,.2f}")
        averages.append(f"{mean:,.2f}")
    return labels, totals, averages


def generate_charts(dataset: Dataset) -> Tuple[List[Dict[str, object]], Dict[str, object]]:
    numeric_columns = [
        col.get("name") for col in (dataset.schema or []) if col.get("semantic_type") == "numeric"
    ]
    categorical_columns = [
        col.get("name") for col in (dataset.schema or []) if col.get("semantic_type") == "categorical"
    ]
    datetime_columns = [
        col.get("name") for col in (dataset.schema or []) if col.get("semantic_type") == "datetime"
    ]

    df = load_dataset_frame(dataset)
    charts: List[Dict[str, object]] = []

    if df.empty:
        layout = {"type": "empty", "message": "Dataset has no rows"}
        return charts, layout

    # KPI summary table
    if numeric_columns:
        labels, totals, averages = _numeric_summary(df, numeric_columns[:4])
    else:
        labels, totals, averages = ["Row count"], [f"{len(df):,}"], ["-"]

    table_fig = go.Figure(
        data=[
            go.Table(
                header=dict(
                    values=["Metric", "Total", "Average"],
                    fill_color="#2563eb",
                    font=dict(color="white"),
                    align="left",
                ),
                cells=dict(
                    values=[labels, totals, averages],
                    align="left",
                ),
            )
        ]
    )
    charts.append(
        {
            "id": "kpi_summary",
            "title": "KPI summary",
            "spec": table_fig.to_dict(),
        }
    )

    # Top categories
    if categorical_columns:
        column = categorical_columns[0]
        counts = (
            df[column]
            .astype(str)
            .replace({"nan": "Unknown"})
            .value_counts()
            .head(10)
            .reset_index()
        )
        counts.columns = [column, "count"]
        cat_fig = px.bar(
            counts,
            x=column,
            y="count",
            title=f"Top categories — {column}",
        )
        charts.append(
            {
                "id": "top_categories",
                "title": f"Top categories — {column}",
                "spec": cat_fig.to_dict(),
            }
        )

    # Time trend
    if datetime_columns:
        df = _coerce_datetime(df, datetime_columns)
        column = datetime_columns[0]
        time_df = df.dropna(subset=[column]).copy()
        if not time_df.empty:
            time_df["period"] = time_df[column].dt.to_period("M").dt.to_timestamp()
            value_column = numeric_columns[0] if numeric_columns else None
            if value_column and value_column in df.columns:
                metric = pd.to_numeric(time_df[value_column], errors="coerce")
                time_series = (
                    pd.DataFrame({"period": time_df["period"], value_column: metric})
                    .groupby("period")
                    .sum()
                    .reset_index()
                )
                trend_fig = px.line(
                    time_series,
                    x="period",
                    y=value_column,
                    title=f"{value_column} over time",
                )
                charts.append(
                    {
                        "id": "time_trend",
                        "title": f"{value_column} over time",
                        "spec": trend_fig.to_dict(),
                    }
                )

    layout = {
        "sections": [
            {"id": "summary", "title": "Summary", "charts": ["kpi_summary"]},
            {"id": "explore", "title": "Explore", "charts": [chart["id"] for chart in charts if chart["id"] != "kpi_summary"]},
        ]
    }
    return charts, layout
