from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ...database import get_db
from ...models import Dataset
from ...schemas.mvp import DashboardGenerateRequest, DashboardGenerateResponse
from ...services.dashboards import generate_charts

router = APIRouter(prefix="/dashboards", tags=["dashboards"])


@router.post("/generate", response_model=DashboardGenerateResponse)
def generate_dashboards(body: DashboardGenerateRequest, db: Session = Depends(get_db)):
    dataset = db.query(Dataset).filter(Dataset.id == body.dataset_id).first()
    if not dataset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "DATASET_NOT_FOUND", "message": "Dataset not found."},
        )

    charts, layout = generate_charts(dataset)
    return DashboardGenerateResponse(charts=charts, layout=layout)
