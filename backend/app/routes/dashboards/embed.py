from os import getenv

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials

from ...api.deps import get_current_user, security, verify_token
from ...models.user import User
from ...metabase.jwt import create_signed_url

router = APIRouter(tags=["dashboards"])

@router.get("/dashboards/embed-url")
async def get_default_dashboard_embed_url(
    current_user: User = Depends(get_current_user),
    creds: HTTPAuthorizationCredentials = Depends(security),
):
    # Derive org_id from your app’s auth token (good tenant isolation)
    payload = verify_token(creds.credentials)
    org_id = payload.get("org_id") if payload else None
    if org_id is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    # Single-dashboard mode (env var)
    dash_id_str = getenv("MB_DASHBOARD_DEFAULT_DASHBOARD_ID")
    if not dash_id_str or not dash_id_str.isdigit():
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="MB_DASHBOARD_DEFAULT_DASHBOARD_ID not set")

    dashboard_id = int(dash_id_str)

    # Any param you set as "Locked" in the Metabase UI must be included here
    url = create_signed_url("dashboard", dashboard_id, params={"org_id": str(org_id)}, expiry_minutes=10)
    return {"url": url}
