from __future__ import annotations

import re
import uuid
from typing import Dict, Tuple

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ...config import settings
from ...database import get_db
from ...jobs import enqueue_validation
from ...models import (
    Upload,
    UploadStatus,
    Workflow,
    WorkflowState,
    WorkflowStep,
    Workspace,
    Dataset,
    User,
)
from ...schemas.mvp import (
    UploadCompleteResponse,
    UploadPresignRequest,
    UploadPresignResponse,
    WorkflowStatusResponse,
)
from ...storage.presign import create_presigned_put

router = APIRouter(prefix="/uploads", tags=["uploads"])

ALLOWED_MIME_TYPES = {
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
}


def _api_error(code: str, message: str, status_code: int = status.HTTP_400_BAD_REQUEST):
    raise HTTPException(status_code=status_code, detail={"code": code, "message": message})


def _sanitize_filename(filename: str) -> str:
    name = filename.strip().replace("\\", "/").split("/")[-1]
    name = re.sub(r"[^A-Za-z0-9._-]", "_", name)
    return name or "upload.xlsx"


def _resolve_workspace(db: Session, workspace_id: int) -> Workspace:
    workspace = db.query(Workspace).filter(Workspace.id == workspace_id).first()
    if workspace:
        return workspace

    owner = db.query(User).first()
    workspace = Workspace(
        id=workspace_id,
        name=f"Workspace {workspace_id}",
        slug=f"workspace-{workspace_id}",
        owner_id=owner.id if owner else None,
    )
    db.add(workspace)
    db.flush()
    return workspace


def _ensure_upload_workflow(db: Session, upload: Upload) -> Workflow:
    workflow = (
        db.query(Workflow)
        .filter(
            Workflow.upload_id == upload.id,
            Workflow.step == WorkflowStep.upload,
        )
        .first()
    )
    if workflow:
        return workflow
    workflow = Workflow(
        workspace_id=upload.workspace_id,
        upload_id=upload.id,
        step=WorkflowStep.upload,
        state=WorkflowState.queued,
        meta={"filename": upload.filename},
    )
    db.add(workflow)
    db.flush()
    return workflow


def _create_step(db: Session, upload: Upload, step: WorkflowStep) -> Workflow:
    workflow = Workflow(
        workspace_id=upload.workspace_id,
        upload_id=upload.id,
        dataset_id=upload.dataset.id if upload.dataset else None,
        step=step,
        state=WorkflowState.queued,
    )
    db.add(workflow)
    db.flush()
    return workflow


def _serialise_workflow(workflow: Workflow) -> Dict[str, str]:
    return {
        "id": str(workflow.id),
        "step": workflow.step.value,
        "state": workflow.state.value,
        "error": workflow.error or "",
    }


def _workflow_summary(db: Session, upload: Upload) -> Dict[str, Dict[str, str]]:
    workflows = (
        db.query(Workflow)
        .filter(Workflow.upload_id == upload.id)
        .all()
    )
    dataset_id = str(upload.dataset.id) if upload.dataset else None
    summary: Dict[str, Dict[str, str]] = {
        "upload": {"step": "upload", "state": "pending", "dataset_id": dataset_id},
        "validate": {"step": "validate", "state": "queued", "dataset_id": dataset_id},
        "ingest": {"step": "ingest", "state": "queued", "dataset_id": dataset_id},
    }
    for wf in workflows:
        workflow_dataset_id = str(wf.dataset_id) if wf.dataset_id else dataset_id
        summary[wf.step.value] = {
            "step": wf.step.value,
            "state": wf.state.value,
            "error": wf.error or "",
            "id": str(wf.id),
            "dataset_id": workflow_dataset_id,
        }
    return summary


@router.post("/presign", response_model=UploadPresignResponse)
def presign_upload(body: UploadPresignRequest, db: Session = Depends(get_db)):
    if body.mime_type not in ALLOWED_MIME_TYPES:
        _api_error("UNSUPPORTED_MIME_TYPE", "Only .xlsx files are supported.")

    public_limit = settings.public_upload_max_mb * 1024 * 1024
    if body.size_bytes > public_limit:
        _api_error(
            "UPLOAD_TOO_LARGE",
            f"Upload must be under {settings.public_upload_max_mb} MB.",
        )

    workspace = _resolve_workspace(db, body.workspace_id)
    owner_id = workspace.owner_id
    if not owner_id:
        owner = db.query(User).first()
        if not owner:
            _api_error("USER_NOT_FOUND", "No user is available to own the upload.", status.HTTP_500_INTERNAL_SERVER_ERROR)
        owner_id = owner.id

    filename = _sanitize_filename(body.filename)
    storage_key = f"uploads/{workspace.id}/{uuid.uuid4()}/{filename}"

    upload = Upload(
        workspace_id=workspace.id,
        user_id=owner_id,
        filename=filename,
        mime_type=body.mime_type,
        size=body.size_bytes,
        object_key=storage_key,
        status=UploadStatus.created,
    )
    db.add(upload)
    db.flush()

    _ensure_upload_workflow(db, upload)
    db.commit()

    presigned = create_presigned_put(storage_key, body.mime_type)
    return UploadPresignResponse(
        upload_id=upload.id,
        storage_key=storage_key,
        url=presigned["url"],
        headers=presigned["headers"],
        max_mb=settings.public_upload_max_mb,
    )


@router.post("/{upload_id}/complete", response_model=UploadCompleteResponse)
def complete_upload(upload_id: int, db: Session = Depends(get_db)):
    upload = db.query(Upload).filter(Upload.id == upload_id).first()
    if not upload:
        _api_error("UPLOAD_NOT_FOUND", "Upload not found.", status.HTTP_404_NOT_FOUND)

    server_limit = settings.server_upload_max_mb * 1024 * 1024
    if upload.size > server_limit:
        _api_error(
            "UPLOAD_TOO_LARGE",
            f"Server limit is {settings.server_upload_max_mb} MB.",
        )

    upload.status = UploadStatus.uploaded
    upload.errors_json = None
    upload.error_message = None

    upload_workflow = _ensure_upload_workflow(db, upload)
    upload_workflow.state = WorkflowState.succeeded
    upload_workflow.progress = 100

    validate_workflow = _create_step(db, upload, WorkflowStep.validate)
    db.commit()

    enqueue_validation(upload.id, str(validate_workflow.id))

    summary = _workflow_summary(db, upload)
    return UploadCompleteResponse(
        upload=summary["upload"],
        validate=summary["validate"],
        ingest=summary["ingest"],
    )


@router.get("/{upload_id}/workflow")
def get_upload_workflow(upload_id: int, db: Session = Depends(get_db)):
    upload = db.query(Upload).filter(Upload.id == upload_id).first()
    if not upload:
        _api_error("UPLOAD_NOT_FOUND", "Upload not found.", status.HTTP_404_NOT_FOUND)
    return _workflow_summary(db, upload)
