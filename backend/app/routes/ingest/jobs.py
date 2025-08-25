from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from pydantic import BaseModel
import uuid

from ...api.deps import get_current_user, verify_token, security
from ...database import get_db
from ...models.user import User
from ...models.uploads import Upload
from ...models.ingestion_jobs import IngestionJob, IngestionJobStatus
from ...models.import_batches import ImportBatch, BatchStatus
from ...observability.events import log_event
from ....worker.tasks.ingest_excel_or_csv import ingest_excel_or_csv

router = APIRouter(prefix="/ingest", tags=["ingest"])


class JobCreateRequest(BaseModel):
    upload_id: int


class JobStatusResponse(BaseModel):
    status: IngestionJobStatus
    error: dict | None = None


@router.post("/jobs", status_code=202)
def create_job(
    data: JobCreateRequest,
    current_user: User = Depends(get_current_user),
    creds: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    payload = verify_token(creds.credentials)
    org_id = payload.get("org_id") if payload else None
    if org_id is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    upload = (
        db.query(Upload)
        .filter(Upload.id == data.upload_id, Upload.org_id == org_id)
        .first()
    )
    if upload is None:
        raise HTTPException(status_code=404, detail="Upload not found")

    batch = ImportBatch(
        id=str(uuid.uuid4()),
        source_system="upload",
        triggered_by_user_id=str(current_user.id),
        status=BatchStatus.queued,
    )
    db.add(batch)
    db.flush()

    job = IngestionJob(
        org_id=org_id,
        upload_id=upload.id,
        import_batch_id=batch.id,
        status=IngestionJobStatus.queued,
    )
    db.add(job)
    db.commit()
    db.refresh(job)

    try:
        ingest_excel_or_csv.delay(job.id)
        log_event("ingest_job_enqueued", job_id=job.id, import_batch_id=batch.id)
    except Exception:
        log_event("ingest_job_enqueue_failed", job_id=job.id, import_batch_id=batch.id)

    return {"job_id": job.id}


@router.get("/jobs/{job_id}", response_model=JobStatusResponse)
def get_job(
    job_id: int,
    current_user: User = Depends(get_current_user),
    creds: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    payload = verify_token(creds.credentials)
    org_id = payload.get("org_id") if payload else None
    if org_id is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    job = (
        db.query(IngestionJob)
        .filter(IngestionJob.id == job_id, IngestionJob.org_id == org_id)
        .first()
    )
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")

    return JobStatusResponse(status=job.status, error=job.error_json)
