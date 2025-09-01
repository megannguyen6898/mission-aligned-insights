from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any, Dict

from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPAuthorizationCredentials

from ..metabase.jwt import create_signed_url
from ..api.deps import get_current_user, security, verify_token
from ..models.user import User

router = APIRouter(prefix="/api", tags=["metabase"])

@dataclass
class Dashboard:
    id: int
    name: str

# Read the single dashboard id from env
_DEFAULT_DASHBOARD_ID = int(os.environ.get("MB_DASHBOARD_DEFAULT_DASHBOARD_ID", "1"))
_DASHBOARDS = [Dashboard(id=_DEFAULT_DASHBOARD_ID, name="Main Dashboard")]

@router.get("/dashboards")
def list_dashboards() -> list[Dict[str, Any]]:
    return [d.__dict__ for d in _DASHBOARDS]

@router.post("/metabase/signed")
def sign_metabase(
    payload: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    creds: HTTPAuthorizationCredentials = Depends(security),
) -> Dict[str, str]:
    # derive org_id from the app token; DO NOT trust client-provided org_id
    token_payload = verify_token(creds.credentials)
    org_id = token_payload.get("org_id") if token_payload else None
    if org_id is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    resource = payload.get("resource")
    resource_id = payload.get("id") or _DEFAULT_DASHBOARD_ID
    expiry = int(payload.get("expiry_minutes", 10))

    if resource != "dashboard":
        raise HTTPException(status_code=400, detail="Unsupported resource")

    # Always inject locked params server-side
    params = {"org_id": str(org_id)}
    url = create_signed_url("dashboard", resource_id, params=params, expiry_minutes=expiry)
    return {"url": url}
