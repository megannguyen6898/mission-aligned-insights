from __future__ import annotations

import logging
from typing import Dict

from botocore.exceptions import ClientError  # type: ignore

from ..config import settings
from .s3_client import get_s3_client

logger = logging.getLogger(__name__)
_cors_configured = False


def _ensure_bucket_cors(client) -> None:
    global _cors_configured
    if _cors_configured:
        return

    bucket = settings.storage_bucket
    if not bucket:
        raise RuntimeError("STORAGE_BUCKET not configured")

    allowed_origins = settings.cors_origins
    cors_rules = [
        {
            "AllowedMethods": ["PUT", "GET", "HEAD"],
            "AllowedOrigins": allowed_origins,
            "AllowedHeaders": ["*"],
            "ExposeHeaders": ["ETag"],
            "MaxAgeSeconds": 3000,
        }
    ]

    try:
        client.put_bucket_cors(
            Bucket=bucket,
            CORSConfiguration={"CORSRules": cors_rules},
        )
    except ClientError as exc:  # pragma: no cover - defensive
        logger.warning("Unable to set bucket CORS: %s", exc, exc_info=True)
    else:
        _cors_configured = True


def create_presigned_put(storage_key: str, content_type: str, expires_in: int = 900) -> Dict[str, str]:
    """Generate a presigned PUT URL and headers for MinIO uploads."""
    client = get_s3_client()
    bucket = settings.storage_bucket
    if not bucket:
        raise RuntimeError("STORAGE_BUCKET not configured")

    _ensure_bucket_cors(client)

    params = {
        "Bucket": bucket,
        "Key": storage_key,
        "ContentType": content_type,
    }

    url = client.generate_presigned_url(
        ClientMethod="put_object",
        Params=params,
        ExpiresIn=expires_in,
    )

    return {
        "url": url,
        "headers": {
            "Content-Type": content_type,
        },
    }


def create_presigned_get(storage_key: str, expires_in: int = 900) -> str:
    """Generate a presigned GET URL."""
    client = get_s3_client()
    bucket = settings.storage_bucket
    if not bucket:
        raise RuntimeError("STORAGE_BUCKET not configured")

    return client.generate_presigned_url(
        ClientMethod="get_object",
        Params={"Bucket": bucket, "Key": storage_key},
        ExpiresIn=expires_in,
    )
