import os
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from ...api.deps import get_current_user, verify_token, security
from ...database import get_db
from ...models.user import User
from ...models.uploads import Upload, UploadStatus
from ...schemas.upload import SignedUrlRequest, SignedUrlResponse
from ...storage.s3_client import get_s3_client

router = APIRouter(prefix="/ingest", tags=["ingest"])

ALLOWED_MIMES = {
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "text/csv",
}
MAX_UPLOAD_MB = int(os.environ.get("MAX_UPLOAD_MB", "25"))
MAX_UPLOAD_BYTES = MAX_UPLOAD_MB * 1024 * 1024


@router.post("/uploads:signed-url", response_model=SignedUrlResponse)
def create_signed_upload_url(
    data: SignedUrlRequest,
    current_user: User = Depends(get_current_user),
    creds: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    if data.mime not in ALLOWED_MIMES:
        raise HTTPException(status_code=415, detail="Unsupported file type")
    if data.size > MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=413, detail="File too large")

    payload = verify_token(creds.credentials)
    org_id = payload.get("org_id") if payload else None
    if org_id is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    upload = Upload(
        org_id=org_id,
        user_id=current_user.id,
        filename=data.filename,
        mime_type=data.mime,
        size=data.size,
        object_key="",
        status=UploadStatus.pending,
    )
    db.add(upload)
    db.commit()
    db.refresh(upload)

    prefix = os.environ.get("S3_UPLOAD_PREFIX", "raw/")
    key = f"{prefix}{upload.id}/{data.filename}"
    upload.object_key = key
    db.commit()

    bucket = os.environ["S3_BUCKET"]
    s3 = get_s3_client()
    fields = {"Content-Type": data.mime}
    conditions = [
        {"Content-Type": data.mime},
        ["content-length-range", 0, MAX_UPLOAD_BYTES],
    ]
    presigned = s3.generate_presigned_post(
        Bucket=bucket,
        Key=key,
        Fields=fields,
        Conditions=conditions,
        ExpiresIn=3600,
    )

    return SignedUrlResponse(
        url=presigned["url"],
        fields=presigned["fields"],
        upload_id=upload.id,
    )
