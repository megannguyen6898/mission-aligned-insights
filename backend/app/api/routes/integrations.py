
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ...database import get_db
from ...models.user import User
from ...api.deps import get_current_user, require_roles
from ...services.integration_service import IntegrationService

router = APIRouter(prefix="/integrations", tags=["integrations"])

@router.post("/xero/connect")
async def connect_xero(
    auth_code: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    integration_service = IntegrationService()
    try:
        result = await integration_service.connect_xero(current_user.id, auth_code, db)
        return {"message": "Xero connected successfully", "integration_id": result.id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/google-sheets/connect")
async def connect_google_sheets(
    auth_code: str,
    spreadsheet_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    integration_service = IntegrationService()
    try:
        result = await integration_service.connect_google_sheets(current_user.id, auth_code, spreadsheet_id, db)
        return {"message": "Google Sheets connected successfully", "integration_id": result.id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/google-docs/connect")
async def connect_google_docs(
    auth_code: str,
    document_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    integration_service = IntegrationService()
    try:
        result = await integration_service.connect_google_docs(current_user.id, auth_code, document_id, db)
        return {"message": "Google Docs connected successfully", "integration_id": result.id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/status")
async def get_integration_status(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    integration_service = IntegrationService()
    status = await integration_service.get_integration_status(current_user.id, db)
    return status

@router.post("/sync")
async def sync_integrations(
    current_user: User = Depends(require_roles(["admin"])),
    db: Session = Depends(get_db)
):
    integration_service = IntegrationService()
    try:
        result = await integration_service.sync_all_integrations(current_user.id, db)
        return {"message": "Sync initiated", "results": result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
