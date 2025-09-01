from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Optional
import requests
from jose import jwt, JWTError
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests

from ..database import get_db
from ..config import settings
from ..models.user import User

security = HTTPBearer()

def verify_token(token: str) -> Optional[dict]:
    # 1) Try Auth0 (RS256)
    if getattr(settings, "auth0_domain", None) and getattr(settings, "auth0_audience", None):
        try:
            jwks_url = f"https://{settings.auth0_domain}/.well-known/jwks.json"
            jwks = requests.get(jwks_url, timeout=5).json()
            unverified_header = jwt.get_unverified_header(token)
            rsa_key = next(
                (
                    {"kty": k["kty"], "kid": k["kid"], "use": k["use"], "n": k["n"], "e": k["e"]}
                    for k in jwks.get("keys", [])
                    if k.get("kid") == unverified_header.get("kid")
                ),
                None,
            )
            if rsa_key:
                return jwt.decode(
                    token,
                    rsa_key,
                    algorithms=["RS256"],
                    audience=settings.auth0_audience,
                    issuer=f"https://{settings.auth0_domain}/",
                )
        except Exception:
            pass  # fall through

    # 2) Try Firebase
    if getattr(settings, "firebase_project_id", None):
        try:
            return id_token.verify_firebase_token(
                token, google_requests.Request(), audience=settings.firebase_project_id
            )
        except Exception:
            pass  # fall through

    # 3) Local HS256 fallback
    algo = getattr(settings, "jwt_algorithm", None) or "HS256"
    for key in filter(None, [getattr(settings, "jwt_secret_key", None),
                             getattr(settings, "secret_key", None)]):
        try:
            return jwt.decode(token, key, algorithms=[algo], options={"verify_aud": False})
        except JWTError:
            continue

    return None


async def get_current_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    token = credentials.credentials
    payload = verify_token(token)
    if payload is None or payload.get("type") != "access":
        raise HTTPException(status_code=401, detail="Could not validate credentials")

    user_id = payload.get("sub")
    if isinstance(user_id, str) and user_id.isdigit():
        user_id = int(user_id)

    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")

    request.state.roles = payload.get("roles", [])
    return user
