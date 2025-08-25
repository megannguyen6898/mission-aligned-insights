from __future__ import annotations

from datetime import datetime, timedelta
from os import getenv
from typing import Any, Dict

from jose import jwt


def create_embed_token(dashboard_id: int, params: Dict[str, Any] | None = None, *,
                        expires_in: timedelta | None = None) -> str:
    """Return a signed Metabase embed token.

    Args:
        dashboard_id: The Metabase dashboard ID to embed.
        params: SQL parameters to pass to the dashboard (used for filtering).
        expires_in: Optional lifetime for the token. Defaults to 10 minutes.
    """
    secret = getenv("METABASE_SECRET_KEY")
    if not secret:
        raise RuntimeError("METABASE_SECRET_KEY is not configured")

    if expires_in is None:
        expires_in = timedelta(minutes=10)

    payload = {
        "resource": {"dashboard": dashboard_id},
        "params": params or {},
        "exp": datetime.utcnow() + expires_in,
    }
    return jwt.encode(payload, secret, algorithm="HS256")
