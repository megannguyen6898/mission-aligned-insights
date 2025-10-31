from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ...database import get_db
from ...jobs import enqueue_ingest
from ...models import Dataset, Workflow, WorkflowState, WorkflowStep
from ...schemas.mvp import WorkflowStatusResponse

router = APIRouter(prefix="/workflows", tags=["workflows"])


@router.get("/{workflow_id}/status", response_model=WorkflowStatusResponse)
def get_workflow_status(workflow_id: uuid.UUID, db: Session = Depends(get_db)):
    workflow = db.query(Workflow).filter(Workflow.id == workflow_id).first()
    if not workflow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "WORKFLOW_NOT_FOUND", "message": "Workflow not found."},
        )
    return WorkflowStatusResponse(
        id=str(workflow.id),
        step=workflow.step.value,
        state=workflow.state.value,
        progress=workflow.progress,
        error=workflow.error,
    )


@router.post("/{dataset_id}/ingest", response_model=WorkflowStatusResponse)
def trigger_ingest(dataset_id: uuid.UUID, db: Session = Depends(get_db)):
    dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
    if not dataset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "DATASET_NOT_FOUND", "message": "Dataset not found."},
        )

    workflow = Workflow(
        workspace_id=dataset.workspace_id,
        upload_id=dataset.upload_id,
        dataset_id=dataset.id,
        step=WorkflowStep.ingest,
        state=WorkflowState.queued,
    )
    db.add(workflow)
    db.commit()

    enqueue_ingest(str(dataset.id), str(workflow.id))

    return WorkflowStatusResponse(
        id=str(workflow.id),
        step=workflow.step.value,
        state=workflow.state.value,
        progress=workflow.progress,
        error=workflow.error,
    )
