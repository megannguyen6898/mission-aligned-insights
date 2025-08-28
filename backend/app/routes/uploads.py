import os
from uuid import uuid4
from typing import Optional

from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from ..api.deps import verify_token, security
from ..auth import require_roles, Role
from ..database import get_db
from ..models.user import User
from ..models.uploads import Upload, UploadStatus
from ..models.ingestion_jobs import IngestionJob, IngestionJobStatus
from ..models.import_batches import ImportBatch, BatchStatus
from ..storage.s3_client import get_s3_client
from ..ingest.validators import validate_template_excel, TEMPLATE_VERSION
from ..schemas.upload import UploadCreateResponse, UploadStatusResponse
from ...worker.tasks.ingest_excel_or_csv import ingest_excel_or_csv

router = APIRouter(prefix="/api/uploads", tags=["uploads"])

FILE_MAX_MB = int(os.getenv("FILE_MAX_MB", "5"))
FILE_MAX_BYTES = FILE_MAX_MB * 1024 * 1024


@router.post("", status_code=201, response_model=UploadCreateResponse)
async def create_upload(
    file: UploadFile = File(...),
    current_user: User = Depends(require_roles([Role.org_member, Role.admin])),
    creds: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    if not file.filename.lower().endswith(".xlsx"):
        raise HTTPException(status_code=400, detail="Only .xlsx files are supported")

    contents = await file.read()
    if len(contents) > FILE_MAX_BYTES:
        raise HTTPException(status_code=400, detail="File too large")

    payload = verify_token(creds.credentials)
    org_id: Optional[int] = payload.get("org_id") if payload else None
    if org_id is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    upload = Upload(
        org_id=org_id,
        user_id=current_user.id,
        filename=file.filename,
        mime_type=file.content_type,
        size=len(contents),
        object_key="",
        status=UploadStatus.pending,
        template_version=TEMPLATE_VERSION,
    )
    db.add(upload)
    db.commit()
    db.refresh(upload)

    prefix = os.getenv("S3_UPLOAD_PREFIX", "uploads/")
    key = f"{prefix}{current_user.id}/{uuid4()}.xlsx"
    upload.object_key = key
    db.commit()

    bucket = os.environ["S3_BUCKET"]
    s3 = get_s3_client()
    s3.put_object(Bucket=bucket, Key=key, Body=contents, ContentType=file.content_type)

    return {"upload_id": upload.id}


@router.get("/{upload_id}", response_model=UploadStatusResponse)
async def get_upload(
    upload_id: int,
    current_user: User = Depends(require_roles([Role.org_member, Role.admin])),
    creds: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    payload = verify_token(creds.credentials)
    org_id = payload.get("org_id") if payload else None
    if org_id is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    upload = (
        db.query(Upload)
        .filter(Upload.id == upload_id, Upload.org_id == org_id)
        .first()
    )
    if upload is None:
        raise HTTPException(status_code=404, detail="Upload not found")

    return {
        "status": upload.status.value,
        "template_version": upload.template_version,
        "errors": upload.errors_json,
    }


@router.post("/{upload_id}/validate", response_model=UploadStatusResponse)
async def validate_upload(
    upload_id: int,
    current_user: User = Depends(require_roles([Role.org_member, Role.admin])),
    creds: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    payload = verify_token(creds.credentials)
    org_id = payload.get("org_id") if payload else None
    if org_id is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    upload = (
        db.query(Upload)
        .filter(Upload.id == upload_id, Upload.org_id == org_id)
        .first()
    )
    if upload is None:
        raise HTTPException(status_code=404, detail="Upload not found")

    bucket = os.environ["S3_BUCKET"]
    s3 = get_s3_client()
    obj = s3.get_object(Bucket=bucket, Key=upload.object_key)
    content = obj["Body"].read()

    errors = validate_template_excel(content)
    if errors:
        upload.status = UploadStatus.failed
        upload.errors_json = errors
    else:
        upload.status = UploadStatus.validated
        upload.errors_json = None
    db.commit()

    return {
        "status": upload.status.value,
        "template_version": upload.template_version,
        "errors": upload.errors_json,
    }


@router.post("/{upload_id}/ingest", status_code=202)
async def ingest_upload(
    upload_id: int,
    current_user: User = Depends(require_roles([Role.org_member, Role.admin])),
    creds: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    payload = verify_token(creds.credentials)
    org_id = payload.get("org_id") if payload else None
    if org_id is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    upload = (
        db.query(Upload)
        .filter(Upload.id == upload_id, Upload.org_id == org_id)
        .first()
    )
    if upload is None:
        raise HTTPException(status_code=404, detail="Upload not found")

    batch = ImportBatch(
        id=str(uuid4()),
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

    ingest_excel_or_csv.delay(job.id)

    return {"job_id": job.id}
