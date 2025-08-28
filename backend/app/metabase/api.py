from __future__ import annotations

import logging
import os
import requests

from ..config import settings

logger = logging.getLogger(__name__)


def sync_schema() -> None:
    """Best-effort sync of the Metabase schema."""
    host = settings.mb_site_url
    user = os.getenv("MB_USER") or os.getenv("MB_USERNAME")
    password = os.getenv("MB_PASSWORD") or os.getenv("MB_PASS")
    if not host or not user or not password:
        logger.info("Metabase credentials not configured; skipping sync")
        return
    try:
        sess = requests.Session()
        resp = sess.post(
            f"{host}/api/session",
            json={"username": user, "password": password},
            timeout=5,
        )
        resp.raise_for_status()
        token = resp.json().get("id")
        if not token:
            return
        headers = {"X-Metabase-Session": token}
        sess.post(f"{host}/api/database/1/sync_schema", headers=headers, timeout=5)
    except Exception as exc:  # pragma: no cover - network failures
        logger.warning("Metabase sync failed: %s", exc)
