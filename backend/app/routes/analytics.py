from __future__ import annotations
from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ..database import get_db
from ..services.analytics_service import AnalyticsService

router = APIRouter(prefix="/api/analytics", tags=["analytics"])
service = AnalyticsService()


@router.get("/kpis")
def get_kpis(
    space_id: str = Query(..., description="Identifier for the organization/space"),
    db: Session = Depends(get_db),
):
    try:
        return service.get_kpis(db, space_id)
    except ValueError as exc:  # pragma: no cover - defensive
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/series")
def get_series(
    space_id: str = Query(..., description="Identifier for the organization/space"),
    metric: str = Query("beneficiaries", description="Comma-separated metric keys"),
    group_by: Optional[str] = Query(
        "year", description="One of year, region, program"
    ),
    time_range: Optional[str] = Query(
        None, description="Optional range formatted as YYYY..YYYY"
    ),
    db: Session = Depends(get_db),
):
    metrics = [m.strip() for m in metric.split(",") if m.strip()]
    try:
        return service.get_series(db, space_id, metrics, group_by, time_range)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
