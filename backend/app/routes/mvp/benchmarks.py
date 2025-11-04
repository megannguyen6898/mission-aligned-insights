from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ...database import get_db
from ...models import BenchmarkProject
from ...schemas.impact import BenchmarkResponse


router = APIRouter(prefix="/benchmarks", tags=["benchmarks"])


@router.get("/{sector}", response_model=BenchmarkResponse)
def get_benchmark_sector(sector: str, db: Session = Depends(get_db)) -> BenchmarkResponse:
    rows = (
        db.query(BenchmarkProject)
        .filter(BenchmarkProject.sector == sector)
        .order_by(BenchmarkProject.metric_id.asc())
        .all()
    )
    metrics_payload = [
        {
            "metric_id": row.metric_id,
            "metric_name": row.metric.name if row.metric else "",
            "mean_value": row.mean_value,
            "std_dev": row.std_dev,
            "sample_size": row.sample_size,
            "source": row.source,
        }
        for row in rows
    ]
    return BenchmarkResponse(sector=sector, metrics=metrics_payload)
