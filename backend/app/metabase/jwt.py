from __future__ import annotations

import os, time, binascii
from typing import Any, Dict, Optional
import hashlib
import jwt  # PyJWT

# Accept either env name; use the browser-facing site ONLY to build URLs (not for signing)
MB_SITE_URL = (os.getenv("MB_PUBLIC_SITE_URL") or os.getenv("MB_SITE_URL") or os.getenv("METABASE_SITE_URL") or "").rstrip("/")

# Secret MUST match Admin -> Settings -> Embedding -> "Embedding secret key"
_SECRET_ENV = os.getenv("MB_EMBED_SECRET_KEY") or os.getenv("METABASE_EMBEDDING_SECRET")
if not _SECRET_ENV:
    raise RuntimeError("MB_EMBED_SECRET_KEY (or METABASE_EMBEDDING_SECRET) must be set.")

# Support secrets that are hex or plain strings
try:
    MB_SECRET_BYTES = binascii.unhexlify(_SECRET_ENV)
except (binascii.Error, ValueError, TypeError):
    MB_SECRET_BYTES = _SECRET_ENV.encode("utf-8")

def create_embed_token(dashboard_id: int | str,
                       params: Optional[Dict[str, Any]] = None,
                       expiry_minutes: int = 10) -> str:
    now = int(time.time())
    payload = {
        "resource": {"dashboard": dashboard_id},
        "params": params or {},
        "iat": now,                         # include iat to be safe
        "exp": now + expiry_minutes * 60,   # default 10 minutes
    }
    return jwt.encode(payload, MB_SECRET_BYTES, algorithm="HS256")

def create_signed_url(dashboard_id: int | str,
                      params: Optional[Dict[str, Any]] = None,
                      expiry_minutes: int = 10,
                      titled: bool = True,
                      bordered: bool = True) -> str:
    token = create_embed_token(dashboard_id, params=params, expiry_minutes=expiry_minutes)
    if not MB_SITE_URL:
        return token  # fallback: caller can build URL
    suffix = f"#titled={'true' if titled else 'false'}&bordered={'true' if bordered else 'false'}"
    return f"{MB_SITE_URL}/embed/dashboard/{token}{suffix}"