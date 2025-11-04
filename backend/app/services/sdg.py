from __future__ import annotations

import json
import re
from collections import defaultdict
from typing import Dict, Iterable, List, Sequence, Tuple

from sqlalchemy.orm import Session

from ..models import (
    AIEvent,
    Dataset,
    Metric,
    MetricMapping,
    MetricSDGMapping,
    SDGGoal,
    SDGIndicator,
    SDGTarget,
)


TOKEN_PATTERN = re.compile(r"[a-zA-Z]{3,}")


def _tokenize(values: Iterable[str | None]) -> set[str]:
    tokens: set[str] = set()
    for value in values:
        if not value:
            continue
        for token in TOKEN_PATTERN.findall(value.lower()):
            tokens.add(token)
    return tokens


def _score_tokens(source: set[str], target: set[str]) -> float:
    if not source or not target:
        return 0.0
    overlap = source & target
    return round(len(overlap) / len(target), 4)


def suggest_sdg_alignment(
    db: Session,
    dataset: Dataset,
    max_indicators: int = 3,
) -> Dict[str, object]:
    confirmed_mappings: Sequence[MetricMapping] = (
        db.query(MetricMapping)
        .filter(
            MetricMapping.dataset_id == dataset.id,
            MetricMapping.confirmed.is_(True),
        )
        .all()
    )

    if not confirmed_mappings:
        return {"dataset_id": str(dataset.id), "goals": []}

    indicators: Sequence[Tuple[SDGIndicator, SDGTarget, SDGGoal]] = (
        db.query(SDGIndicator, SDGTarget, SDGGoal)
        .join(SDGTarget, SDGIndicator.target_id == SDGTarget.id)
        .join(SDGGoal, SDGTarget.goal_id == SDGGoal.id)
        .all()
    )

    indicator_tokens: Dict[int, set[str]] = {
        indicator.id: _tokenize([indicator.title, indicator.description, target.title, goal.title])
        for indicator, target, goal in indicators
    }

    goal_results: Dict[int, Dict[str, object]] = defaultdict(
        lambda: {"score": 0.0, "targets": {}, "goal": None}
    )
    mapping_events: List[Dict[str, object]] = []

    for mapping in confirmed_mappings:
        metric: Metric = mapping.metric
        if not metric:
            continue
        metric_tokens = _tokenize(
            [
                metric.name,
                metric.code,
                metric.category,
                mapping.column_name,
                mapping.column_sample,
            ]
        )
        ranked: List[Tuple[float, SDGIndicator, SDGTarget, SDGGoal]] = []
        for indicator, target, goal in indicators:
            score = _score_tokens(metric_tokens, indicator_tokens[indicator.id])
            if score > 0:
                ranked.append((score, indicator, target, goal))

        ranked.sort(key=lambda entry: entry[0], reverse=True)
        top_ranked = ranked[:max_indicators]
        mapping_events.append(
            {
                "metric_id": metric.id,
                "column": mapping.column_name,
                "matched_indicators": [
                    {"indicator_id": indicator.id, "score": score}
                    for score, indicator, *_ in top_ranked
                ],
            }
        )

        for score, indicator, target, goal in top_ranked:
            goal_bucket = goal_results[goal.id]
            goal_bucket["goal"] = goal
            target_bucket = goal_bucket["targets"].setdefault(
                target.id,
                {
                    "target": target,
                    "indicators": [],
                    "score": 0.0,
                },
            )
            target_bucket["indicators"].append(
                {
                    "indicator": indicator,
                    "metric_id": metric.id,
                    "dataset_column": mapping.column_name,
                    "score": score,
                }
            )
            target_bucket["score"] = max(target_bucket["score"], score)
            goal_bucket["score"] = max(goal_bucket["score"], score)

            _persist_metric_indicator_mapping(db, metric.id, indicator.id, score)

    response_goals: List[Dict[str, object]] = []
    for goal_data in goal_results.values():
        goal: SDGGoal = goal_data["goal"]
        if goal is None:
            continue
        targets_payload: List[Dict[str, object]] = []
        for target_data in goal_data["targets"].values():
            target: SDGTarget = target_data["target"]
            indicators_payload: List[Dict[str, object]] = []
            for indicator_payload in target_data["indicators"]:
                indicator: SDGIndicator = indicator_payload["indicator"]
                indicators_payload.append(
                    {
                        "indicator_id": indicator.id,
                        "indicator_code": indicator.code,
                        "indicator_title": indicator.title,
                        "score": indicator_payload["score"],
                        "metric_id": indicator_payload["metric_id"],
                        "dataset_column": indicator_payload["dataset_column"],
                    }
                )
            targets_payload.append(
                {
                    "target_id": target.id,
                    "target_code": target.code,
                    "target_title": target.title,
                    "score": target_data["score"],
                    "indicators": indicators_payload,
                }
            )

        response_goals.append(
            {
                "goal_id": goal.id,
                "goal_number": goal.number,
                "goal_title": goal.title,
                "goal_color": goal.color,
                "score": goal_data["score"],
                "targets": targets_payload,
            }
        )

    response_goals.sort(key=lambda item: item["score"], reverse=True)
    _log_sdg_event(db, dataset, mapping_events, response_goals)

    return {"dataset_id": str(dataset.id), "goals": response_goals}


def _persist_metric_indicator_mapping(db: Session, metric_id: int, indicator_id: int, score: float) -> None:
    record = (
        db.query(MetricSDGMapping)
        .filter(
            MetricSDGMapping.metric_id == metric_id,
            MetricSDGMapping.indicator_id == indicator_id,
        )
        .first()
    )
    if record is None:
        record = MetricSDGMapping(
            metric_id=metric_id,
            indicator_id=indicator_id,
            relevance_score=score,
        )
        db.add(record)
    else:
        record.relevance_score = max(record.relevance_score, score)
    db.commit()


def _log_sdg_event(
    db: Session,
    dataset: Dataset,
    mapping_events: Sequence[Dict[str, object]],
    goals: Sequence[Dict[str, object]],
) -> None:
    workspace_id = dataset.workspace_id or (dataset.workspace.id if dataset.workspace else None)
    if not workspace_id:
        return
    event = AIEvent(
        workspace_id=workspace_id,
        dataset_id=dataset.id,
        question="SDG alignment suggestion",
        answer=json.dumps(
            {
                "mappings": mapping_events,
                "goals": [
                    {
                        "goal_number": goal["goal_number"],
                        "score": goal["score"],
                    }
                    for goal in goals[:5]
                ],
            }
        ),
    )
    db.add(event)
    db.commit()
