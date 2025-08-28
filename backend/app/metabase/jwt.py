"""Utilities for signing Metabase embed URLs."""

from __future__ import annotations

from datetime import datetime, timedelta
from os import getenv
from typing import Any, Dict

from jose import jwt

from ..config import settings


def _create_token(
    resource: str,
    resource_id: int,
    params: Dict[str, Any] | None = None,
    *,
    expires_in: timedelta | None = None,
) -> str:
    """Return a signed JWT for embedding a Metabase resource."""

    secret = settings.mb_encryption_secret or getenv("METABASE_SECRET_KEY")  # type: ignore[name-defined]
    if not secret:
        raise RuntimeError("Metabase embedding secret is not configured")

    if expires_in is None:
        expires_in = timedelta(minutes=10)

    payload = {
        "resource": {resource: resource_id},
        "params": params or {},
        "exp": datetime.utcnow() + expires_in,
    }
    return jwt.encode(payload, secret, algorithm="HS256")


def create_embed_token(
    dashboard_id: int,
    params: Dict[str, Any] | None = None,
    *,
    expires_in: timedelta | None = None,
) -> str:
    """Backwards compatible helper for dashboard tokens."""

    return _create_token("dashboard", dashboard_id, params, expires_in=expires_in)


def create_signed_url(
    resource: str,
    resource_id: int,
    params: Dict[str, Any] | None = None,
    *,
    expiry_minutes: int = 10,
) -> str:
    """Generate a full iframe URL for an embedded Metabase resource."""

    token = _create_token(
        resource,
        resource_id,
        params,
        expires_in=timedelta(minutes=expiry_minutes),
    )
    site = settings.mb_site_url or getenv("MB_SITE_URL")  # type: ignore[name-defined]
    if not site:
        raise RuntimeError("MB_SITE_URL is not configured")
    return f"{site}/embed/{resource}/{token}#bordered=true&titled=true"
