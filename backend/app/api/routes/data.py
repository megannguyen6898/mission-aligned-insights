
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
from ...database import get_db
from ...schemas.data import DataUploadResponse, DataUploadRequest
from ...models.data_upload import DataUpload, SourceType, UploadStatus
from ...models.user import User
from ...models.audit_log import AuditLog, AuditAction
from ...api.deps import get_current_user
from ...services.data_service import DataService
from ...services.ingestion_service import IngestionService

router = APIRouter(prefix="/data", tags=["data"])

@router.post("/upload", response_model=DataUploadResponse)
async def upload_data(
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    upload_dir = Path("uploads")
    upload_dir.mkdir(exist_ok=True)

    data_upload = DataUpload(
        user_id=current_user.id,
        file_name=file.filename,
        source_type=SourceType.manual,
        status=UploadStatus.pending,
    )
    db.add(data_upload)
    db.commit()
    db.refresh(data_upload)

    file_path = upload_dir / f"{data_upload.id}_{file.filename}"
    with open(file_path, "wb") as buffer:
        buffer.write(await file.read())
    data_upload.file_path = str(file_path)
    db.commit()
    db.refresh(data_upload)

    ingestion_service = IngestionService()
    background_tasks.add_task(ingestion_service.ingest_upload, data_upload.id, db)

    return data_upload

@router.get("/uploads", response_model=List[DataUploadResponse])
async def get_uploads(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    uploads = db.query(DataUpload).filter(DataUpload.user_id == current_user.id).all()
    return uploads

@router.delete("/uploads/{upload_id}")
async def delete_upload(
    upload_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    upload = db.query(DataUpload).filter(
        DataUpload.id == upload_id,
        DataUpload.user_id == current_user.id
    ).first()

    if not upload:
        raise HTTPException(status_code=404, detail="Upload not found")

    log = AuditLog(
        user_id=current_user.id,
        action=AuditAction.delete,
        target_type="data_upload",
        target_id=upload.id,
        details=f"Deleted upload {upload.file_name}",
    )
    db.add(log)
    db.commit()

    db.delete(upload)
    db.commit()

    return {"message": "Upload deleted successfully"}

@router.post("/validate")
async def validate_data(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    data_service = DataService()
    try:
        validation_result = await data_service.validate_data_file(file)
        return validation_result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
