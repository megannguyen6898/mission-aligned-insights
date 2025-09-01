from __future__ import annotations

import os
import time
import binascii
from typing import Any, Dict, Optional

import jwt  # PyJWT

_MB_SITE_URL = os.getenv("MB_SITE_URL", "").rstrip("/")
_MB_SECRET_HEX = os.getenv("MB_EMBED_SECRET_KEY")

if not _MB_SITE_URL or not _MB_SECRET_HEX:
    raise RuntimeError("MB_SITE_URL and MB_EMBED_SECRET_KEY must be set.")

# Metabase shows a 256-bit secret as 64-char hex; sign with raw bytes
try:
    _MB_SECRET_BYTES = binascii.unhexlify(_MB_SECRET_HEX)
except Exception as e:
    raise RuntimeError("MB_EMBED_SECRET_KEY must be a 64-char hex string.") from e


def create_embed_token(dashboard_id: int | str,
                       params: Optional[Dict[str, Any]] = None,
                       expiry_minutes: int = 10) -> str:
    payload = {
        "resource": {"dashboard": dashboard_id},
        "params": params or {},
        "exp": int(time.time()) + (expiry_minutes * 60),
    }
    return jwt.encode(payload, _MB_SECRET_BYTES, algorithm="HS256")


def create_signed_url(resource: str,
                      resource_id: int | str,
                      params: Optional[Dict[str, Any]] = None,
                      expiry_minutes: int = 10,
                      titled: bool = True,
                      bordered: bool = True) -> str:
    if resource != "dashboard":
        raise ValueError("Only 'dashboard' embedding is supported.")
    token = create_embed_token(resource_id, params=params, expiry_minutes=expiry_minutes)
    suffix = f"#titled={'true' if titled else 'false'}&bordered={'true' if bordered else 'false'}"
    return f"{_MB_SITE_URL}/embed/{resource}/{token}{suffix}"
