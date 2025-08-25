from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from fastapi.security import HTTPAuthorizationCredentials
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ..api.deps import get_current_user, verify_token, security
from ..database import get_db
from ..models.user import User
from ..reports.generate import generate_pdf

class ReportRequest(BaseModel):
    project_id: str
    sections: list[str]

router = APIRouter(tags=["reports"])

@router.post("/reports:generate")
async def create_report(
    data: ReportRequest,
    current_user: User = Depends(get_current_user),
    creds: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    payload = verify_token(creds.credentials)
    org_id = payload.get("org_id") if payload else None
    if org_id is None:
        raise HTTPException(status_code=401, detail="Invalid token")

    pdf_path = generate_pdf(data.project_id, org_id, data.sections, db)
    if not pdf_path.exists():
        raise HTTPException(status_code=500, detail="Failed to generate report")

    return FileResponse(
        pdf_path,
        media_type="application/pdf",
        filename=pdf_path.name,
    )
