from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from ..api.deps import get_current_user, verify_token, security
from ..database import get_db
from ..models.user import User
from ..audit.model import AuditEvent

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/audit-events")
def list_audit_events(
    org_id: int,
    current_user: User = Depends(get_current_user),
    creds: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    payload = verify_token(creds.credentials)
    token_org = payload.get("org_id") if payload else None
    if token_org is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    if "admin" not in getattr(current_user, "roles", []):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")

    events = (
        db.query(AuditEvent)
        .filter(AuditEvent.org_id == org_id)
        .order_by(AuditEvent.created_at.desc())
        .limit(100)
        .all()
    )
    return [
        {
            "id": e.id,
            "created_at": e.created_at,
            "action": e.action,
            "user_id": e.user_id,
            "org_id": e.org_id,
            "project_id": e.project_id,
            "upload_id": e.upload_id,
            "job_id": e.job_id,
            "batch_id": e.batch_id,
            "data": e.data,
        }
        for e in events
    ]
