from __future__ import annotations

import math
from typing import Dict, Iterable, List, Sequence

import pandas as pd
from statistics import NormalDist
from sqlalchemy.orm import Session

from ..models import (
    CorrelationResult,
    Dataset,
    MetricMapping,
    MetricSDGMapping,
)
from .dashboards import load_dataset_frame


def _pearson_correlation(x: pd.Series, y: pd.Series) -> float:
    if x.empty or y.empty:
        return float("nan")
    return float(x.corr(y))


def _approximate_p_value(r: float, n: int) -> float:
    if n <= 3 or math.isclose(abs(r), 1.0):
        return 0.0
    z = abs(r) * math.sqrt(n - 3)
    normal = NormalDist()
    return round(2 * (1 - normal.cdf(z)), 6)


def _classify_direction(r: float) -> str:
    if r >= 0.6:
        return "Direct Positive"
    if 0.2 <= r < 0.6:
        return "Indirect Positive"
    if -0.2 < r < 0.2:
        return "Neutral"
    if -0.6 < r <= -0.2:
        return "Indirect Negative"
    return "Direct Negative"


class ImpactAnalyticsService:
    def run_correlations(
        self,
        db: Session,
        dataset: Dataset,
        independent_variables: Sequence[str],
        min_overlap: int = 10,
    ) -> List[CorrelationResult]:
        df = load_dataset_frame(dataset)
        if df.empty:
            return []

        confirmed_mappings: Sequence[MetricMapping] = (
            db.query(MetricMapping)
            .filter(
                MetricMapping.dataset_id == dataset.id,
                MetricMapping.confirmed.is_(True),
            )
            .all()
        )
        independent_variables = [col for col in independent_variables if col in df.columns]
        if not confirmed_mappings or not independent_variables:
            return []

        results: List[CorrelationResult] = []
        db.query(CorrelationResult).filter(CorrelationResult.dataset_id == dataset.id).delete()

        sdg_lookup: Dict[int, int] = {}
        mapping_rows: Sequence[MetricSDGMapping] = (
            db.query(MetricSDGMapping)
            .filter(MetricSDGMapping.metric_id.in_([m.metric_id for m in confirmed_mappings]))
            .all()
        )
        for mapping in mapping_rows:
            sdg_lookup[mapping.metric_id] = mapping.indicator_id

        for mapping in confirmed_mappings:
            metric_series = pd.to_numeric(df[mapping.column_name], errors="coerce").dropna()
            if metric_series.empty:
                continue
            for variable in independent_variables:
                variable_series = pd.to_numeric(df[variable], errors="coerce").dropna()
                combined = pd.concat([metric_series, variable_series], axis=1, join="inner").dropna()
                combined.columns = ["metric", "independent"]
                if combined.shape[0] < min_overlap:
                    continue
                r_value = _pearson_correlation(combined["metric"], combined["independent"])
                if math.isnan(r_value):
                    continue
                p_value = _approximate_p_value(r_value, combined.shape[0])
                confidence = min(abs(r_value) * (combined.shape[0] / (combined.shape[0] + 5)), 0.99)
                result = CorrelationResult(
                    dataset_id=dataset.id,
                    metric_id=mapping.metric_id,
                    sdg_indicator_id=sdg_lookup.get(mapping.metric_id),
                    independent_variable=variable,
                    r_value=r_value,
                    p_value=p_value,
                    direction=_classify_direction(r_value),
                    confidence=confidence,
                )
                db.add(result)
                results.append(result)

        db.commit()
        return results

    def get_results(self, db: Session, dataset: Dataset) -> List[CorrelationResult]:
        return (
            db.query(CorrelationResult)
            .filter(CorrelationResult.dataset_id == dataset.id)
            .order_by(CorrelationResult.confidence.desc())
            .all()
        )
