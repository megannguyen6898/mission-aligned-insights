
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from ...database import get_db
from ...models.user import User
from ...api.deps import get_current_user
from ...services.report_service import ReportService

router = APIRouter(prefix="/reports", tags=["reports"])

@router.get("/frameworks")
async def get_reporting_frameworks():
    frameworks = [
        {"id": "sdg", "name": "Sustainable Development Goals", "description": "UN SDG framework"},
        {"id": "esg", "name": "Environmental, Social, Governance", "description": "ESG reporting framework"},
        {"id": "b_impact", "name": "B Impact Assessment", "description": "B Corp impact framework"},
        {"id": "gri", "name": "Global Reporting Initiative", "description": "GRI sustainability standards"}
    ]
    return {"frameworks": frameworks}

@router.post("/generate")
async def generate_report(
    framework: str,
    title: str = "Impact Report",
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    report_service = ReportService()
    try:
        report = await report_service.generate_report(
            current_user.id, framework, title, db
        )
        return {"message": "Report generated successfully", "report_id": report.id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{report_id}")
async def get_report(
    report_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    report_service = ReportService()
    report = await report_service.get_report(report_id, current_user.id, db)
    
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    return report

@router.get("/{report_id}/download")
async def download_report(
    report_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    report_service = ReportService()
    try:
        pdf_path = await report_service.generate_pdf(report_id, current_user.id, db)
        return FileResponse(
            pdf_path,
            media_type="application/pdf",
            filename=f"report_{report_id}.pdf",
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
