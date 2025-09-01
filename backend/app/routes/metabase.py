from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any, Dict, Optional

from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPAuthorizationCredentials
from pydantic import BaseModel

# Use your existing helpers
from ..metabase.jwt import create_signed_url, create_embed_token
from ..api.deps import get_current_user, security, verify_token
from ..models.user import User

router = APIRouter(prefix="/api", tags=["metabase"])

@dataclass
class Dashboard:
    id: int
    name: str

# Support both env names; prefer MB_DASHBOARD_ID if present
_DEFAULT_DASHBOARD_ID = int(
    os.getenv("MB_DASHBOARD_DEFAULT_DASHBOARD_ID", "2")
)

_DASHBOARDS = [Dashboard(id=_DEFAULT_DASHBOARD_ID, name="Main Dashboard")]

@router.get("/dashboards")
def list_dashboards() -> list[Dict[str, Any]]:
    return [d.__dict__ for d in _DASHBOARDS]


class SignReq(BaseModel):
    # Support BOTH payload styles:
    # 1) {"resource": {"dashboard": 2}, "params": {...}}
    # 2) {"resource": "dashboard", "id": 2, "params": {...}}  (legacy)
    resource: Optional[Dict[str, Any] | str] = None
    id: Optional[int] = None
    params: Optional[Dict[str, Any]] = None
    expiry_minutes: int = 10


@router.post("/metabase/signed")
def sign_metabase(
    req: SignReq,
    current_user: User = Depends(get_current_user),
    creds: HTTPAuthorizationCredentials = Depends(security),
) -> Dict[str, str]:
    # Derive org_id: prefer token payload; fall back to current_user if available.
    org_id: Optional[str] = None
    token_payload = verify_token(creds.credentials)
    if token_payload and "org_id" in token_payload:
        org_id = str(token_payload["org_id"])
    elif getattr(current_user, "org_id", None) is not None:
        org_id = str(current_user.org_id)

    # If you REQUIRE org_id for locked params, keep this; otherwise comment it out.
    # if org_id is None:
    #     raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token: missing org_id")

    # Resolve dashboard id from either payload style or env default
    dashboard_id: Optional[int | str] = None
    if isinstance(req.resource, dict):
        dashboard_id = req.resource.get("dashboard")
    elif isinstance(req.resource, str):
        if req.resource != "dashboard":
            raise HTTPException(status_code=400, detail="Unsupported resource")
        dashboard_id = req.id
    if dashboard_id is None:
        dashboard_id = _DEFAULT_DASHBOARD_ID

    # Merge client params with locked params (locked wins)
    locked = {"org_id": org_id} if org_id is not None else {}
    params = {**(req.params or {}), **locked}

    # Produce BOTH jwt and url (frontend can choose which it wants)
    token = create_embed_token(dashboard_id, params=params, expiry_minutes=req.expiry_minutes)
    site = (os.getenv("MB_SITE_URL") or os.getenv("METABASE_SITE_URL") or "").rstrip("/")
    url = f"{site}/embed/dashboard/{token}#titled=true&bordered=true" if site else ""

    return {"jwt": token, "url": url}
