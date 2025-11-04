from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ...database import get_db
from ...models import Dataset
from ...schemas.mvp import ReportGenerateRequest, ReportGenerateResponse
from ...services.dashboards import generate_charts
from ...services.report import generate_report
from ...services.sdg import suggest_sdg_alignment
from ...services.analytics import ImpactAnalyticsService

router = APIRouter(prefix="/reports", tags=["reports"])


@router.post("/generate", response_model=ReportGenerateResponse)
def generate(body: ReportGenerateRequest, db: Session = Depends(get_db)):
    dataset = db.query(Dataset).filter(Dataset.id == body.dataset_id).first()
    if not dataset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "DATASET_NOT_FOUND", "message": "Dataset not found."},
        )

    charts, _layout = generate_charts(dataset)
    if body.selected_chart_ids:
        charts = [chart for chart in charts if chart["id"] in body.selected_chart_ids]

    sdg_summary = suggest_sdg_alignment(db, dataset)
    analytics_service = ImpactAnalyticsService()
    correlation_rows = analytics_service.get_results(db, dataset)
    correlation_payload = [
        {
            "metric_id": row.metric_id,
            "sdg_indicator_id": row.sdg_indicator_id,
            "independent_variable": row.independent_variable,
            "r_value": row.r_value,
            "p_value": row.p_value,
            "direction": row.direction,
            "confidence": row.confidence,
        }
        for row in correlation_rows
    ]

    result = generate_report(
        dataset=dataset,
        charts=charts,
        narratives=[block.model_dump() for block in body.narrative_blocks],
        branding=body.branding.model_dump() if body.branding else None,
        sdg_summary=sdg_summary,
        correlations=correlation_payload,
    )

    return ReportGenerateResponse(
        report_id=result["report_id"],
        download_url=result["download_url"],
    )
