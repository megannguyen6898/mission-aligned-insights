from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ...database import get_db
from ...models import Dataset
from ...schemas.mvp import DatasetResponse
from ...schemas.impact import (
    AnalysisResultsResponse,
    AnalysisRunRequest,
    AnalysisRunResponse,
    MetricConfirmRequest,
    MetricConfirmResponse,
    MetricSuggestRequest,
    MetricSuggestResponse,
    SDGSuggestResponse,
)
from ...services.metrics import suggest_metric_mappings, confirm_metric_mappings
from ...services.sdg import suggest_sdg_alignment
from ...services.analytics import ImpactAnalyticsService
from ...jobs import enqueue_analysis_job

router = APIRouter(prefix="/datasets", tags=["datasets"])
analytics_service = ImpactAnalyticsService()


@router.get("/{dataset_id}", response_model=DatasetResponse)
def get_dataset(dataset_id: uuid.UUID, db: Session = Depends(get_db)):
    dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
    if not dataset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "DATASET_NOT_FOUND", "message": "Dataset not found."},
        )
    return DatasetResponse(
        schema=dataset.schema or [],
        preview=dataset.preview or [],
        row_count=dataset.row_count,
        table_name=dataset.table_name,
    )


@router.post("/{dataset_id}/metrics/suggest", response_model=MetricSuggestResponse)
def suggest_metrics(
    dataset_id: uuid.UUID,
    body: MetricSuggestRequest = MetricSuggestRequest(),
    db: Session = Depends(get_db),
) -> MetricSuggestResponse:
    dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
    if not dataset:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dataset not found")
    result = suggest_metric_mappings(db, dataset, limit=body.top_n)
    return MetricSuggestResponse(**result)


@router.post("/{dataset_id}/metrics/confirm", response_model=MetricConfirmResponse)
def confirm_metrics(
    dataset_id: uuid.UUID,
    body: MetricConfirmRequest,
    db: Session = Depends(get_db),
) -> MetricConfirmResponse:
    dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
    if not dataset:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dataset not found")
    records = confirm_metric_mappings(
        db,
        dataset,
        [mapping.model_dump() for mapping in body.mappings],
    )
    return MetricConfirmResponse(
        dataset_id=str(dataset.id),
        confirmed=[record.column_name for record in records],
    )


@router.get("/{dataset_id}/sdg/suggest", response_model=SDGSuggestResponse)
def suggest_sdg(dataset_id: uuid.UUID, db: Session = Depends(get_db)) -> SDGSuggestResponse:
    dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
    if not dataset:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dataset not found")
    result = suggest_sdg_alignment(db, dataset)
    return SDGSuggestResponse(**result)


@router.post("/{dataset_id}/analysis/run", response_model=AnalysisRunResponse)
def run_analysis(
    dataset_id: uuid.UUID,
    body: AnalysisRunRequest,
    db: Session = Depends(get_db),
) -> AnalysisRunResponse:
    dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
    if not dataset:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dataset not found")
    job = enqueue_analysis_job(str(dataset.id), body.independent_variables)
    status_label = "queued" if job else "skipped"
    job_id = job.id if job else None
    if not job:
        analytics_service.run_correlations(db, dataset, body.independent_variables)
    return AnalysisRunResponse(dataset_id=str(dataset.id), job_id=job_id, status=status_label)


@router.get("/{dataset_id}/analysis/results", response_model=AnalysisResultsResponse)
def analysis_results(dataset_id: uuid.UUID, db: Session = Depends(get_db)) -> AnalysisResultsResponse:
    dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
    if not dataset:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dataset not found")
    results = analytics_service.get_results(db, dataset)
    return AnalysisResultsResponse(
        dataset_id=str(dataset.id),
        results=[
            {
                "correlation_id": str(result.id),
                "metric_id": result.metric_id,
                "sdg_indicator_id": result.sdg_indicator_id,
                "independent_variable": result.independent_variable,
                "r_value": result.r_value,
                "p_value": result.p_value,
                "direction": result.direction,
                "confidence": result.confidence,
            }
            for result in results
        ],
    )
