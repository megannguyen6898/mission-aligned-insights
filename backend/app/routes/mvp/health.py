from __future__ import annotations

import httpx
from fastapi import APIRouter

from ...config import settings
from ...database import SessionLocal
from ...storage.s3_client import get_s3_client

router = APIRouter(tags=["health"])


@router.get("/healthz")
def healthcheck():
    db_ok = False
    redis_ok = False
    storage_ok = False
    ai_ok = False

    # Database
    session = SessionLocal()
    try:
        session.execute("SELECT 1")
        db_ok = True
    finally:
        session.close()

    # Redis
    try:
        import redis

        redis.Redis.from_url(settings.redis_url).ping()
        redis_ok = True
    except Exception:
        redis_ok = False

    # MinIO / Storage
    try:
        client = get_s3_client()
        bucket = settings.storage_bucket
        if bucket:
            client.head_bucket(Bucket=bucket)
            storage_ok = True
    except Exception:
        storage_ok = False

    # AI (Ollama)
    if settings.use_local_model:
        try:
            endpoint = settings.ollama_endpoint or "http://ollama:11434"
            resp = httpx.get(f"{endpoint.rstrip('/')}/api/tags", timeout=4)
            resp.raise_for_status()
            ai_ok = True
        except Exception:
            ai_ok = False
    else:
        ai_ok = False

    return {
        "database": db_ok,
        "redis": redis_ok,
        "storage": storage_ok,
        "ai": ai_ok,
    }
