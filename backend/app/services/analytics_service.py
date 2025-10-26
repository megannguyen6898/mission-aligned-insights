from __future__ import annotations

import uuid
from datetime import date
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

from sqlalchemy import func
from sqlalchemy.orm import Session

from ..models import (
    Activity,
    Beneficiary,
    FundingResource,
    Project,
    Outcome,
    ActivityOutcomeFact,
)


class AnalyticsService:
    """Service for refreshing and querying analytics facts."""

    def refresh_facts(self, db: Session) -> None:
        db.query(ActivityOutcomeFact).delete()
        db.commit()

        rows = (
            db.query(
                Activity.project_fk.label("project_fk"),
                Activity.date.label("activity_date"),
                func.count(Activity.id).label("activities"),
                func.coalesce(func.sum(Beneficiary.count), 0).label("beneficiaries"),
                func.coalesce(func.sum(FundingResource.spent), 0).label("spend"),
            )
            .outerjoin(
                Beneficiary,
                (Beneficiary.project_fk == Activity.project_fk)
                & (Beneficiary.date == Activity.date),
            )
            .outerjoin(
                FundingResource,
                (FundingResource.project_fk == Activity.project_fk)
                & (FundingResource.date == Activity.date),
            )
            .group_by(Activity.project_fk, Activity.date)
        ).all()

        for r in rows:
            db.add(
                ActivityOutcomeFact(
                    id=str(uuid.uuid4()),
                    project_fk=r.project_fk,
                    activity_date=r.activity_date,
                    activities=r.activities or 0,
                    beneficiaries=int(r.beneficiaries or 0),
                    spend=float(r.spend or 0.0),
                )
            )
        db.commit()

    # KPI values
    def kpis(self, db: Session, org_id: str, start: date | None = None) -> Dict[str, Any]:
        q = (
            db.query(
                func.count(func.distinct(ActivityOutcomeFact.project_fk)).label("projects"),
                func.coalesce(func.sum(ActivityOutcomeFact.beneficiaries), 0).label("beneficiaries"),
                func.coalesce(func.sum(ActivityOutcomeFact.spend), 0).label("spend"),
                func.coalesce(func.sum(ActivityOutcomeFact.activities), 0).label("activities"),
            )
            .join(Project, Project.id == ActivityOutcomeFact.project_fk)
            .filter(Project.owner_org_id == org_id)
        )
        if start is not None:
            q = q.filter(ActivityOutcomeFact.activity_date >= start)
        res = q.one()
        return {
            "projects": int(res.projects or 0),
            "beneficiaries": int(res.beneficiaries or 0),
            "spend": float(res.spend or 0.0),
            "activities": int(res.activities or 0),
        }

    def activity_series(self, db: Session, org_id: str, start: date, end: date) -> List[Dict[str, Any]]:
        dialect = db.bind.dialect.name  # type: ignore[attr-defined]
        if dialect == "sqlite":
            month_expr = func.strftime("%Y-%m-01", ActivityOutcomeFact.activity_date)
        else:
            month_expr = func.date_trunc("month", ActivityOutcomeFact.activity_date)

        q = (
            db.query(
                month_expr.label("month"),
                func.sum(ActivityOutcomeFact.activities).label("value"),
            )
            .join(Project, Project.id == ActivityOutcomeFact.project_fk)
            .filter(Project.owner_org_id == org_id)
            .filter(ActivityOutcomeFact.activity_date >= start)
            .filter(ActivityOutcomeFact.activity_date <= end)
            .group_by(month_expr)
            .order_by(month_expr)
        )
        results = []
        for r in q.all():
            if isinstance(r.month, str):
                month = r.month
            else:
                month = r.month.date().isoformat()  # type: ignore[call-arg]
            results.append({"month": month, "value": int(r.value or 0)})
        return results

    # ------------------------------------------------------------------ #
    # New analytics API helpers
    # ------------------------------------------------------------------ #

    _METRIC_DEFINITIONS: Dict[str, Dict[str, Any]] = {
        "beneficiaries": {
            "label": "Beneficiaries",
            "unit": "people",
            "facts_field": ActivityOutcomeFact.beneficiaries,
        },
        "completions": {
            "label": "Completions",
            "unit": "people",
            "facts_field": ActivityOutcomeFact.activities,
        },
        "volunteers": {
            "label": "Volunteers",
            "unit": "people",
            "funding_field": FundingResource.volunteer_hours,
        },
        "spend": {
            "label": "Spend",
            "unit": "USD",
            "facts_field": ActivityOutcomeFact.spend,
        },
        "stipends": {
            "label": "Stipends",
            "unit": "USD",
            "funding_field": FundingResource.spent,
            "funding_filter": lambda q: q.filter(
                func.lower(FundingResource.funding_source).contains("stipend")
            ),
        },
        "placement_rate": {
            "label": "Placement Rate",
            "unit": "ratio",
            "derived": True,
        },
        "satisfaction": {
            "label": "Satisfaction",
            "unit": "score",
            "outcome_pattern": "%satisfaction%",
        },
    }

    _VALID_GROUPINGS = {"year", "region", "program"}

    def get_kpis(self, db: Session, space_id: str) -> Dict[str, Any]:
        """Return dynamic KPI list for a space."""
        kpis: List[Dict[str, Any]] = []
        beneficiaries_value = self._sum_facts(
            db, space_id, ActivityOutcomeFact.beneficiaries
        )
        completions_value = self._sum_facts(
            db, space_id, ActivityOutcomeFact.activities
        )

        for key, definition in self._METRIC_DEFINITIONS.items():
            if key == "placement_rate":
                value = (
                    completions_value / beneficiaries_value
                    if beneficiaries_value
                    else 0.0
                )
                delta = self._delta_ratio(
                    db,
                    space_id,
                    ActivityOutcomeFact.activities,
                    ActivityOutcomeFact.beneficiaries,
                )
            else:
                value = self._compute_metric_value(db, space_id, key, definition)
                delta = self._compute_metric_delta(db, space_id, key, definition)

            kpis.append(
                {
                    "label": definition["label"],
                    "value": float(value or 0),
                    "delta": float(delta),
                    "unit": definition["unit"],
                }
            )

        return {"kpis": kpis}

    def get_series(
        self,
        db: Session,
        space_id: str,
        metrics: Sequence[str],
        group_by: Optional[str],
        time_range: Optional[str],
    ) -> Dict[str, Any]:
        normalized_metrics = [m.strip() for m in metrics if m.strip()]
        if not normalized_metrics:
            normalized_metrics = ["beneficiaries"]

        if group_by is None:
            group_by = "year"

        if group_by not in self._VALID_GROUPINGS:
            raise ValueError(f"Unsupported group_by: {group_by}")

        date_bounds = self._parse_time_range(time_range)

        series_payload: List[Dict[str, Any]] = []
        for metric in normalized_metrics:
            definition = self._METRIC_DEFINITIONS.get(metric)
            if not definition:
                raise ValueError(f"Unsupported metric: {metric}")
            points = self._compute_series_points(
                db, space_id, group_by, date_bounds, metric, definition
            )
            series_payload.append({"label": definition["label"], "points": points})

        meta = {
            "unit": (
                self._METRIC_DEFINITIONS.get(normalized_metrics[0], {}).get("unit")
                if normalized_metrics
                else None
            ),
            "note": "space-scoped; aggregation derived from normalized ingestion facts",
        }
        return {"series": series_payload, "meta": meta}

    # ------------------------------------------------------------------ #
    # Internal helpers
    # ------------------------------------------------------------------ #

    def _sum_facts(self, db: Session, space_id: str, column) -> float:
        res = (
            db.query(func.coalesce(func.sum(column), 0.0))
            .join(Project, Project.id == ActivityOutcomeFact.project_fk)
            .filter(Project.owner_org_id == space_id)
            .scalar()
        )
        return float(res or 0.0)

    def _sum_funding(
        self,
        db: Session,
        space_id: str,
        column,
        extra_filter=None,
        date_bounds: Optional[Tuple[Optional[date], Optional[date]]] = None,
    ) -> float:
        query = (
            db.query(func.coalesce(func.sum(column), 0.0))
            .join(Project, Project.id == FundingResource.project_fk)
            .filter(Project.owner_org_id == space_id)
        )
        if date_bounds:
            start, end = date_bounds
            if start is not None:
                query = query.filter(FundingResource.date >= start)
            if end is not None:
                query = query.filter(FundingResource.date <= end)
        if extra_filter is not None:
            query = extra_filter(query)
        return float(query.scalar() or 0.0)

    def _average_outcome(
        self,
        db: Session,
        space_id: str,
        pattern: str,
        date_bounds: Optional[Tuple[Optional[date], Optional[date]]] = None,
    ) -> float:
        query = (
            db.query(func.avg(Outcome.value))
            .join(Project, Project.id == Outcome.project_fk)
            .filter(Project.owner_org_id == space_id)
            .filter(func.lower(Outcome.outcome_metric).like(pattern))
        )
        if date_bounds:
            start, end = date_bounds
            if start is not None:
                query = query.filter(Outcome.date >= start)
            if end is not None:
                query = query.filter(Outcome.date <= end)
        return float(query.scalar() or 0.0)

    def _compute_metric_value(
        self,
        db: Session,
        space_id: str,
        metric: str,
        definition: Dict[str, Any],
    ) -> float:
        if "facts_field" in definition:
            return self._sum_facts(db, space_id, definition["facts_field"])
        if "funding_field" in definition:
            return self._sum_funding(
                db,
                space_id,
                definition["funding_field"],
                definition.get("funding_filter"),
            )
        if "outcome_pattern" in definition:
            return self._average_outcome(
                db, space_id, definition["outcome_pattern"]
            )
        return 0.0

    def _compute_metric_delta(
        self,
        db: Session,
        space_id: str,
        metric: str,
        definition: Dict[str, Any],
    ) -> float:
        if "facts_field" in definition:
            return self._delta_from_series(db, space_id, definition["facts_field"])
        if "funding_field" in definition:
            return self._delta_from_funding(
                db,
                space_id,
                definition["funding_field"],
                definition.get("funding_filter"),
            )
        if "outcome_pattern" in definition:
            return self._delta_from_outcomes(
                db, space_id, definition["outcome_pattern"]
            )
        return 0.0

    def _delta_from_series(self, db: Session, space_id: str, column) -> float:
        records = self._time_series_for_column(db, space_id, column)
        if len(records) < 2:
            return 0.0
        previous = records[-2][1]
        current = records[-1][1]
        if previous in (None, 0):
            return 1.0 if current else 0.0
        return (current - previous) / previous

    def _delta_ratio(
        self, db: Session, space_id: str, numerator, denominator
    ) -> float:
        numerator_series = dict(self._time_series_for_column(db, space_id, numerator))
        denominator_series = dict(self._time_series_for_column(db, space_id, denominator))
        if not numerator_series or not denominator_series:
            return 0.0
        ordered_periods = sorted(set(numerator_series) & set(denominator_series))
        if len(ordered_periods) < 2:
            return 0.0
        prev_period = ordered_periods[-2]
        curr_period = ordered_periods[-1]
        prev = denominator_series[prev_period]
        curr = denominator_series[curr_period]
        prev_ratio = (
            numerator_series.get(prev_period, 0) / prev if prev else 0.0
        )
        curr_ratio = (
            numerator_series.get(curr_period, 0) / curr if curr else 0.0
        )
        if prev_ratio == 0:
            return 1.0 if curr_ratio else 0.0
        return (curr_ratio - prev_ratio) / prev_ratio

    def _delta_from_funding(
        self, db: Session, space_id: str, column, extra_filter=None
    ) -> float:
        records = self._time_series_for_funding(
            db, space_id, column, extra_filter
        )
        if len(records) < 2:
            return 0.0
        previous = records[-2][1]
        current = records[-1][1]
        if previous in (None, 0):
            return 1.0 if current else 0.0
        return (current - previous) / previous

    def _delta_from_outcomes(
        self, db: Session, space_id: str, pattern: str
    ) -> float:
        records = self._time_series_for_outcomes(db, space_id, pattern)
        if len(records) < 2:
            return 0.0
        previous = records[-2][1]
        current = records[-1][1]
        if previous in (None, 0):
            return 1.0 if current else 0.0
        return (current - previous) / previous

    def _time_series_for_column(
        self, db: Session, space_id: str, column
    ) -> List[Tuple[str, float]]:
        period_expr = self._month_bucket_expr(db, ActivityOutcomeFact.activity_date)
        query = (
            db.query(
                period_expr.label("period"),
                func.coalesce(func.sum(column), 0.0).label("value"),
            )
            .join(Project, Project.id == ActivityOutcomeFact.project_fk)
            .filter(Project.owner_org_id == space_id)
            .filter(ActivityOutcomeFact.activity_date.isnot(None))
            .group_by(period_expr)
            .order_by(period_expr)
        )
        rows = []
        for period, value in query.all():
            rows.append((self._normalize_period(period), float(value or 0.0)))
        return rows

    def _time_series_for_funding(
        self, db: Session, space_id: str, column, extra_filter=None
    ) -> List[Tuple[str, float]]:
        period_expr = self._month_bucket_expr(db, FundingResource.date)
        query = (
            db.query(
                period_expr.label("period"),
                func.coalesce(func.sum(column), 0.0).label("value"),
            )
            .join(Project, Project.id == FundingResource.project_fk)
            .filter(Project.owner_org_id == space_id)
            .filter(FundingResource.date.isnot(None))
            .group_by(period_expr)
            .order_by(period_expr)
        )
        if extra_filter is not None:
            query = extra_filter(query)
        rows = []
        for period, value in query.all():
            rows.append((self._normalize_period(period), float(value or 0.0)))
        return rows

    def _time_series_for_outcomes(
        self, db: Session, space_id: str, pattern: str
    ) -> List[Tuple[str, float]]:
        period_expr = self._month_bucket_expr(db, Outcome.date)
        query = (
            db.query(
                period_expr.label("period"),
                func.coalesce(func.avg(Outcome.value), 0.0).label("value"),
            )
            .join(Project, Project.id == Outcome.project_fk)
            .filter(Project.owner_org_id == space_id)
            .filter(Outcome.date.isnot(None))
            .filter(func.lower(Outcome.outcome_metric).like(pattern))
            .group_by(period_expr)
            .order_by(period_expr)
        )
        rows = []
        for period, value in query.all():
            rows.append((self._normalize_period(period), float(value or 0.0)))
        return rows

    def _compute_series_points(
        self,
        db: Session,
        space_id: str,
        group_by: str,
        date_bounds: Optional[Tuple[Optional[date], Optional[date]]],
        metric: str,
        definition: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        if "facts_field" in definition or metric == "placement_rate":
            rows = self._group_facts(
                db,
                space_id,
                group_by,
                date_bounds,
                definition.get("facts_field"),
            )
            if metric == "placement_rate":
                beneficiaries = dict(
                    self._group_facts(
                        db,
                        space_id,
                        group_by,
                        date_bounds,
                        ActivityOutcomeFact.beneficiaries,
                    )
                )
                completions = dict(
                    self._group_facts(
                        db,
                        space_id,
                        group_by,
                        date_bounds,
                        ActivityOutcomeFact.activities,
                    )
                )
                points = []
                for bucket in sorted(set(beneficiaries) | set(completions)):
                    denom = beneficiaries.get(bucket, 0.0)
                    num = completions.get(bucket, 0.0)
                    ratio = num / denom if denom else 0.0
                    points.append({"x": bucket, "y": ratio})
                return points
            return [{"x": bucket, "y": value} for bucket, value in rows]

        if "funding_field" in definition:
            rows = self._group_funding(
                db,
                space_id,
                group_by,
                date_bounds,
                definition["funding_field"],
                definition.get("funding_filter"),
            )
            return [{"x": bucket, "y": value} for bucket, value in rows]

        if "outcome_pattern" in definition:
            rows = self._group_outcomes(
                db,
                space_id,
                group_by,
                date_bounds,
                definition["outcome_pattern"],
            )
            return [{"x": bucket, "y": value} for bucket, value in rows]

        return []

    def _group_facts(
        self,
        db: Session,
        space_id: str,
        group_by: str,
        date_bounds: Optional[Tuple[Optional[date], Optional[date]]],
        column,
    ) -> List[Tuple[Any, float]]:
        if column is None:
            column = ActivityOutcomeFact.activities

        grouping_expr = self._grouping_expression(
            db, group_by, ActivityOutcomeFact.activity_date
        )
        query = (
            db.query(
                grouping_expr.label("bucket"),
                func.coalesce(func.sum(column), 0.0).label("value"),
            )
            .join(Project, Project.id == ActivityOutcomeFact.project_fk)
            .filter(Project.owner_org_id == space_id)
        )
        if date_bounds:
            start, end = date_bounds
            if start is not None:
                query = query.filter(ActivityOutcomeFact.activity_date >= start)
            if end is not None:
                query = query.filter(ActivityOutcomeFact.activity_date <= end)
        query = query.group_by(grouping_expr).order_by(grouping_expr)
        return [
            (self._normalize_bucket(bucket), float(value or 0.0))
            for bucket, value in query.all()
        ]

    def _group_funding(
        self,
        db: Session,
        space_id: str,
        group_by: str,
        date_bounds: Optional[Tuple[Optional[date], Optional[date]]],
        column,
        extra_filter=None,
    ) -> List[Tuple[Any, float]]:
        grouping_expr = self._grouping_expression(
            db, group_by, FundingResource.date
        )
        query = (
            db.query(
                grouping_expr.label("bucket"),
                func.coalesce(func.sum(column), 0.0).label("value"),
            )
            .join(Project, Project.id == FundingResource.project_fk)
            .filter(Project.owner_org_id == space_id)
        )
        if date_bounds:
            start, end = date_bounds
            if start is not None:
                query = query.filter(FundingResource.date >= start)
            if end is not None:
                query = query.filter(FundingResource.date <= end)
        if extra_filter is not None:
            query = extra_filter(query)
        query = query.group_by(grouping_expr).order_by(grouping_expr)
        return [
            (self._normalize_bucket(bucket), float(value or 0.0))
            for bucket, value in query.all()
        ]

    def _group_outcomes(
        self,
        db: Session,
        space_id: str,
        group_by: str,
        date_bounds: Optional[Tuple[Optional[date], Optional[date]]],
        pattern: str,
    ) -> List[Tuple[Any, float]]:
        grouping_expr = self._grouping_expression(db, group_by, Outcome.date)
        query = (
            db.query(
                grouping_expr.label("bucket"),
                func.coalesce(func.avg(Outcome.value), 0.0).label("value"),
            )
            .join(Project, Project.id == Outcome.project_fk)
            .filter(Project.owner_org_id == space_id)
            .filter(func.lower(Outcome.outcome_metric).like(pattern))
        )
        if date_bounds:
            start, end = date_bounds
            if start is not None:
                query = query.filter(Outcome.date >= start)
            if end is not None:
                query = query.filter(Outcome.date <= end)
        query = query.group_by(grouping_expr).order_by(grouping_expr)
        return [
            (self._normalize_bucket(bucket), float(value or 0.0))
            for bucket, value in query.all()
        ]

    def _grouping_expression(self, db: Session, group_by: str, date_column):
        if group_by == "year":
            dialect = db.bind.dialect.name  # type: ignore[attr-defined]
            if dialect == "sqlite":
                return func.strftime("%Y", date_column)
            return func.extract("year", date_column)
        if group_by == "region":
            return func.coalesce(Project.region, "Unknown")
        if group_by == "program":
            return func.coalesce(Project.name, Project.project_id)
        raise ValueError(f"Unsupported group_by: {group_by}")

    def _month_bucket_expr(self, db: Session, column):
        dialect = db.bind.dialect.name  # type: ignore[attr-defined]
        if dialect == "sqlite":
            return func.strftime("%Y-%m-01", column)
        return func.date_trunc("month", column)

    def _normalize_period(self, value: Any) -> str:
        if isinstance(value, str):
            return value
        if hasattr(value, "date"):
            return value.date().isoformat()
        if isinstance(value, (int, float)):
            return str(int(value))
        return str(value)

    def _normalize_bucket(self, value: Any) -> Any:
        if value is None:
            return "Unknown"
        if isinstance(value, float) and value.is_integer():
            return int(value)
        return value

    def _parse_time_range(
        self, time_range: Optional[str]
    ) -> Optional[Tuple[Optional[date], Optional[date]]]:
        if not time_range:
            return None
        try:
            start_str, end_str = time_range.split("..")
            start = date(int(start_str), 1, 1)
            end = date(int(end_str), 12, 31)
            if start > end:
                start, end = end, start
            return (start, end)
        except Exception:
            raise ValueError("time_range must be formatted as YYYY..YYYY")
