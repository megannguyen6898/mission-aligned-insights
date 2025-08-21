
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
from ...database import get_db
from ...schemas.data import DataUploadResponse, DataUploadRequest
from ...models.data_upload import DataUpload, SourceType, UploadStatus
from ...models.audit_log import AuditLog
from ...models.user import User
from ...api.deps import get_current_user
from ...services.data_service import DataService

router = APIRouter(prefix="/data", tags=["data"])

@router.post("/upload", response_model=DataUploadResponse)
async def upload_data(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Create data upload record
    data_upload = DataUpload(
        user_id=current_user.id,
        file_name=file.filename,
        source_type=SourceType.manual,
        status=UploadStatus.processing
    )
    
    db.add(data_upload)
    db.commit()
    db.refresh(data_upload)
    
    # Process file using DataService
    data_service = DataService()
    try:
        result = await data_service.process_uploaded_file(file, data_upload.id, db)
        data_upload.status = UploadStatus.completed
        data_upload.row_count = result.get("row_count", 0)
    except Exception as e:
        data_upload.status = UploadStatus.failed
        data_upload.error_message = str(e)
    
    db.commit()
    db.refresh(data_upload)
    
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
        action="delete",
        resource_type="data_upload",
        resource_id=upload.id,
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
