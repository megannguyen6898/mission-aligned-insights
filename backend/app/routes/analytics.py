from __future__ import annotations

from datetime import date, timedelta
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ..database import get_db
from ..services.analytics_service import AnalyticsService

router = APIRouter(prefix="/api/analytics", tags=["analytics"])
service = AnalyticsService()


@router.get("/kpis")
def get_kpis(org_id: str, range: str = "last_90d", db: Session = Depends(get_db)):
    start: date | None = None
    if range == "last_90d":
        start = date.today() - timedelta(days=90)
    elif range not in ("all", ""):
        raise HTTPException(status_code=400, detail="Unsupported range")
    return service.kpis(db, org_id, start)


@router.get("/series")
def get_series(
    metric: str,
    org_id: str,
    from_: date = Query(..., alias="from"),
    to: date = Query(...),
    db: Session = Depends(get_db),
):
    if metric != "activities_by_month":
        raise HTTPException(status_code=400, detail="Unsupported metric")
    return service.activity_series(db, org_id, from_, to)
