from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from pydantic import BaseModel

from ...api.deps import get_current_user, verify_token, security
from ...database import get_db
from ...models.user import User
from ...models.project import Project
from ....worker.tasks.recompute_metrics import recompute_metrics as recompute_metrics_task

router = APIRouter(tags=["metrics"])


class RecomputeRequest(BaseModel):
    project_id: str | None = None


@router.post("/metrics:recompute")
def recompute_metrics_endpoint(
    data: RecomputeRequest,
    current_user: User = Depends(get_current_user),
    creds: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    payload = verify_token(creds.credentials)
    org_id = payload.get("org_id") if payload else None
    if org_id is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    user_roles = getattr(current_user, "roles", [])
    is_admin = "admin" in user_roles

    if data.project_id:
        project = (
            db.query(Project)
            .filter(Project.id == data.project_id, Project.owner_org_id == str(org_id))
            .first()
        )
        if project is None:
            raise HTTPException(status_code=404, detail="Project not found")
        counts = recompute_metrics_task(org_id=str(org_id), project_id=project.id)
        return counts
    else:
        if not is_admin:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
        counts = recompute_metrics_task(org_id=str(org_id))
        return counts
