from os import getenv

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials

from ...api.deps import get_current_user, security, verify_token
from ...models.user import User
from ...metabase.jwt import create_embed_token

router = APIRouter(tags=["dashboards"])


def _dashboard_id_from_slug(slug: str) -> int | None:
    env_var = f"METABASE_DASHBOARD_{slug.replace('-', '_').upper()}_ID"
    value = getenv(env_var)
    return int(value) if value and value.isdigit() else None


@router.get("/dashboards/{slug}/embed-token")
async def get_dashboard_embed_token(
    slug: str,
    current_user: User = Depends(get_current_user),
    creds: HTTPAuthorizationCredentials = Depends(security),
):
    payload = verify_token(creds.credentials)
    org_id = payload.get("org_id") if payload else None
    if org_id is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    dashboard_id = _dashboard_id_from_slug(slug)
    if dashboard_id is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Unknown dashboard")

    token = create_embed_token(dashboard_id, {"org_id": str(org_id)})
    return {"token": token}
