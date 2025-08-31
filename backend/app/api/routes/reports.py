
import os
from typing import Any, Dict, Optional

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    UploadFile,
    File,
    Form,
    Response,
)
from fastapi.security import HTTPAuthorizationCredentials
from fastapi.responses import FileResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ...database import get_db
from ...models.user import User
from ...api.deps import get_current_user, verify_token, security
from ...models.report import (
    ReportTemplate,
    ReportJob,
    ReportJobStatus,
    ReportEngine,
)
from ...storage.s3_client import get_s3_client

router = APIRouter(prefix="/reports", tags=["reports"])
templates_router = APIRouter(prefix="/report-templates", tags=["report-templates"])


class ReportCreateRequest(BaseModel):
    template_id: int
    params: Optional[Dict[str, Any]] = None

@router.get("/frameworks")
async def get_reporting_frameworks():
    frameworks = [
        {"id": "sdg", "name": "Sustainable Development Goals", "description": "UN SDG framework"},
        {"id": "esg", "name": "Environmental, Social, Governance", "description": "ESG reporting framework"},
        {"id": "b_impact", "name": "B Impact Assessment", "description": "B Corp impact framework"},
        {"id": "gri", "name": "Global Reporting Initiative", "description": "GRI sustainability standards"}
    ]
    return {"frameworks": frameworks}

@templates_router.post("", status_code=201)
async def create_report_template(
    file: UploadFile = File(...),
    name: str = Form(...),
    description: str = Form(""),
    engine: ReportEngine = Form(...),
    version: int = Form(1),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    contents = await file.read()
    template = ReportTemplate(
        name=name,
        description=description,
        engine=engine,
        object_key="",
        version=version,
        created_by=current_user.id,
    )
    db.add(template)
    db.commit()
    db.refresh(template)

    key = f"report-templates/{template.id}/{file.filename}"
    bucket = os.environ["S3_BUCKET"]
    s3 = get_s3_client()
    s3.put_object(Bucket=bucket, Key=key, Body=contents, ContentType=file.content_type)
    template.object_key = key
    db.commit()
    return {"template_id": template.id}


@templates_router.get("")
async def list_report_templates(db: Session = Depends(get_db)):
    templates = db.query(ReportTemplate).all()
    return {
        "templates": [
            {
                "id": t.id,
                "name": t.name,
                "description": t.description,
                "engine": t.engine.value,
                "version": t.version,
            }
            for t in templates
        ]
    }


@router.post("", status_code=201)
async def create_report_job(
    data: ReportCreateRequest,
    current_user: User = Depends(get_current_user),
    creds: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    payload = verify_token(creds.credentials)
    org_id: Optional[str] = payload.get("org_id") if payload else None
    if org_id is None:
        raise HTTPException(status_code=401, detail="Invalid token")

    job = ReportJob(
        user_id=current_user.id,
        org_id=str(org_id),
        template_id=data.template_id,
        params_json=data.params or {},
        status=ReportJobStatus.queued,
    )
    db.add(job)
    db.commit()
    db.refresh(job)

    try:
        from worker.tasks.render_report import render_report_job

        render_report_job.delay(job.id)
    except Exception:
        pass

    return {"report_id": job.id}


@router.get("/{job_id}")
async def get_report_job(
    job_id: int,
    current_user: User = Depends(get_current_user),
    creds: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    payload = verify_token(creds.credentials)
    org_id: Optional[str] = payload.get("org_id") if payload else None
    job = (
        db.query(ReportJob)
        .filter(
            ReportJob.id == job_id,
            ReportJob.user_id == current_user.id,
            ReportJob.org_id == str(org_id),
        )
        .first()
    )
    if job is None:
        raise HTTPException(status_code=404, detail="Report not found")
    return {"status": job.status.value, "error": job.error_json}


@router.get("/{job_id}/download")
async def download_report_job(
    job_id: int,
    current_user: User = Depends(get_current_user),
    creds: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    payload = verify_token(creds.credentials)
    org_id: Optional[str] = payload.get("org_id") if payload else None
    job = (
        db.query(ReportJob)
        .filter(
            ReportJob.id == job_id,
            ReportJob.user_id == current_user.id,
            ReportJob.org_id == str(org_id),
        )
        .first()
    )
    if job is None or not job.output_object_key:
        raise HTTPException(status_code=404, detail="Report not ready")

    bucket = os.environ["S3_BUCKET"]
    s3 = get_s3_client()
    obj = s3.get_object(Bucket=bucket, Key=job.output_object_key)
    content = obj["Body"].read()
    filename = job.output_object_key.split("/")[-1]
    media_type = "application/pdf" if filename.endswith(".pdf") else "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    return Response(
        content,
        media_type=media_type,
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )
