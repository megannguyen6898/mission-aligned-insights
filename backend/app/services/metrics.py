from __future__ import annotations
from difflib import SequenceMatcher
from statistics import mean, stdev
from typing import Dict, List, Sequence

import pandas as pd
from sqlalchemy.orm import Session

from ..models import AIEvent, Dataset, Metric, MetricMapping
from .dashboards import load_dataset_frame


def _string_similarity(a: str, b: str) -> float:
    if not a or not b:
        return 0.0
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()


def _summarise_column(df: pd.DataFrame, column: str) -> Dict[str, object]:
    if column not in df:
        return {}

    series = df[column]
    sample_values = [str(v) for v in series.dropna().head(5).tolist()]
    summary: Dict[str, object] = {"sample_values": sample_values}

    numeric = pd.to_numeric(series, errors="coerce")
    numeric = numeric.dropna()
    if not numeric.empty:
        summary["mean"] = float(numeric.mean())
        summary["std_dev"] = float(numeric.std()) if len(numeric) > 1 else 0.0
        summary["non_null_ratio"] = float(len(numeric) / max(len(series), 1))
    else:
        summary["non_null_ratio"] = float(series.dropna().shape[0] / max(len(series), 1))

    return summary


def _confidence_from_summary(metric: Metric, summary: Dict[str, object]) -> float:
    base = 0.0
    if summary.get("non_null_ratio", 0) > 0.8:
        base += 0.2
    if summary.get("mean") is not None:
        base += 0.2
    if summary.get("std_dev") is not None and summary.get("std_dev") != 0:
        base += 0.1
    if metric.unit:
        base += 0.1
    return min(base, 0.4)


def suggest_metric_mappings(
    db: Session,
    dataset: Dataset,
    limit: int = 3,
) -> Dict[str, object]:
    df = load_dataset_frame(dataset)
    library_metrics: Sequence[Metric] = (
        db.query(Metric)
        .filter(Metric.is_library.is_(True))
        .order_by(Metric.name.asc())
        .all()
    )

    columns_to_analyse = [col.get("name") for col in (dataset.schema or []) if col.get("name")]
    existing = {
        mapping.column_name: mapping
        for mapping in dataset.metric_mappings or []
    }

    suggestions: List[Dict[str, object]] = []
    for column in columns_to_analyse:
        column_summary = _summarise_column(df, column)
        ranked: List[Dict[str, object]] = []

        for metric in library_metrics:
            name_similarity = _string_similarity(column, metric.name)
            code_similarity = _string_similarity(column, metric.code or "")
            label_similarity = max(name_similarity, code_similarity)
            confidence = 0.6 * label_similarity + _confidence_from_summary(metric, column_summary)
            if metric.category and column.lower().startswith(metric.category.lower()):
                confidence += 0.1
            confidence = round(min(confidence, 0.99), 3)
            ranked.append(
                {
                    "metric_id": metric.id,
                    "metric_name": metric.name,
                    "metric_code": metric.code,
                    "unit": metric.unit,
                    "confidence": confidence,
                    "similarity": round(label_similarity, 3),
                    "category": metric.category,
                }
            )

        ranked.sort(key=lambda item: item["confidence"], reverse=True)
        suggestions.append(
            {
                "column_name": column,
                "existing_mapping": existing.get(column).metric_id if column in existing else None,
                "summary": column_summary,
                "suggestions": ranked[:limit],
            }
        )

    _log_mapping_event(
        db,
        dataset,
        "AI metric mapping suggestion",
        {
            "columns": len(columns_to_analyse),
            "library_metrics": len(library_metrics),
        },
    )

    return {"dataset_id": str(dataset.id), "columns": suggestions}


def confirm_metric_mappings(
    db: Session,
    dataset: Dataset,
    mappings: Sequence[Dict[str, object]],
) -> List[MetricMapping]:
    df = load_dataset_frame(dataset)
    confirmed_records: List[MetricMapping] = []
    for mapping in mappings:
        column_name = mapping["column_name"]
        metric_id = mapping["metric_id"]
        confidence = mapping.get("confidence")
        suggested = mapping.get("suggested_by_ai", False)
        summary = _summarise_column(df, column_name)
        sample_values = summary.get("sample_values") or []
        sample_preview = ", ".join(sample_values[:3])

        record = (
            db.query(MetricMapping)
            .filter(
                MetricMapping.dataset_id == dataset.id,
                MetricMapping.column_name == column_name,
            )
            .first()
        )
        if record is None:
            record = MetricMapping(
                dataset_id=dataset.id,
                column_name=column_name,
                metric_id=metric_id,
                confidence=confidence,
                suggested_by_ai=bool(suggested),
                column_sample=sample_preview or None,
                confirmed=True,
            )
            db.add(record)
        else:
            record.metric_id = metric_id
            record.confidence = confidence
            record.confirmed = True
            record.suggested_by_ai = bool(suggested or record.suggested_by_ai)
            if sample_preview:
                record.column_sample = sample_preview
        confirmed_records.append(record)

    db.commit()

    _log_mapping_event(
        db,
        dataset,
        "Metric mappings confirmed",
        {
            "confirmed_columns": [m.column_name for m in confirmed_records],
        },
    )
    return confirmed_records


def _log_mapping_event(db: Session, dataset: Dataset, title: str, payload: Dict[str, object]) -> None:
    workspace_id = dataset.workspace_id or (dataset.workspace.id if dataset.workspace else None)
    if not workspace_id:
        return
    event = AIEvent(
        workspace_id=workspace_id,
        dataset_id=dataset.id,
        question=title,
        answer=pd.Series(payload).to_json(),
    )
    db.add(event)
    db.commit()
