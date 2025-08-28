from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any, Dict

from fastapi import APIRouter, HTTPException

from ..metabase.jwt import create_signed_url

router = APIRouter(prefix="/api", tags=["metabase"])


@dataclass
class Dashboard:
    id: int
    name: str


_DEFAULT_DASHBOARD_ID = int(os.environ.get("MB_DEFAULT_DASHBOARD_ID", "1"))
_DASHBOARDS = [Dashboard(id=_DEFAULT_DASHBOARD_ID, name="Main Dashboard")]


@router.get("/dashboards")
def list_dashboards() -> list[Dict[str, Any]]:
    return [d.__dict__ for d in _DASHBOARDS]


@router.post("/metabase/signed")
def sign_metabase(payload: Dict[str, Any]) -> Dict[str, str]:
    resource = payload.get("resource")
    resource_id = payload.get("id")
    params = payload.get("params")
    expiry = payload.get("expiry_minutes", 10)
    if resource != "dashboard" or not isinstance(resource_id, int):
        raise HTTPException(status_code=400, detail="Unsupported resource")
    url = create_signed_url(resource, resource_id, params=params, expiry_minutes=expiry)
    return {"url": url}
