from __future__ import annotations

from ..config import settings

try:
    import boto3  # type: ignore
    from botocore.client import Config  # type: ignore
except ImportError as exc:  # pragma: no cover - defensive fallback
    raise RuntimeError("boto3 is required for storage operations") from exc


def get_s3_client():
    """Create an S3 client configured for AWS S3 or MinIO."""
    endpoint_url = settings.storage_endpoint
    region = settings.storage_region
    access_key = settings.storage_access_key
    secret_key = settings.storage_secret_key
    provider = (settings.storage_provider or "s3").lower()

    kwargs = {}
    if endpoint_url:
        kwargs["endpoint_url"] = endpoint_url
    if region:
        kwargs["region_name"] = region
    if access_key and secret_key:
        kwargs["aws_access_key_id"] = access_key
        kwargs["aws_secret_access_key"] = secret_key

    if provider == "minio":
        kwargs["config"] = Config(signature_version="s3v4")

    return boto3.client("s3", **kwargs)
