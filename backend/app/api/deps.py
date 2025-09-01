from fastapi import Depends, HTTPException, status
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
    """Verify JWT via Auth0 (RS256), Firebase, or local HS256 (fallback)."""
    # 1) Auth0 (RS256)
    if settings.auth0_domain and settings.auth0_audience:
        jwks_url = f"https://{settings.auth0_domain}/.well-known/jwks.json"
        try:
            jwks = requests.get(jwks_url, timeout=5).json()
            unverified_header = jwt.get_unverified_header(token)
        except Exception:
            return None

        rsa_key = {}
        for key in jwks.get("keys", []):
            if key.get("kid") == unverified_header.get("kid"):
                rsa_key = {
                    "kty": key["kty"],
                    "kid": key["kid"],
                    "use": key["use"],
                    "n": key["n"],
                    "e": key["e"],
                }
                break
        if not rsa_key:
            return None

        try:
            payload = jwt.decode(
                token,
                rsa_key,
                algorithms=["RS256"],
                audience=settings.auth0_audience,
                issuer=f"https://{settings.auth0_domain}/",
            )
            return payload
        except JWTError:
            return None

    # 2) Firebase
    if settings.firebase_project_id:
        try:
            return id_token.verify_firebase_token(
                token,
                google_requests.Request(),
                audience=settings.firebase_project_id,
            )
        except Exception:
            return None

    # 3) Local HS256 fallback (matches your /api/v1/auth/login)
    for key in [settings.jwt_secret_key, settings.secret_key]:
        if not key:
            continue
        try:
            payload = jwt.decode(
                token,
                key,
                algorithms=[settings.jwt_algorithm or "HS256"],
                options={"verify_aud": False},
            )
            return payload
        except JWTError:
            continue
    return None


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    token = credentials.credentials
    payload = verify_token(token)

    if payload is None or payload.get("type") != "access":
        raise HTTPException(status_code=401, detail="Could not validate credentials")

    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(status_code=401, detail="Could not validate credentials")

    # Accept "6" (str) or 6 (int)
    if isinstance(user_id, str) and user_id.isdigit():
        user_id = int(user_id)

    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")

    user.roles = payload.get("roles", [])
    return user
