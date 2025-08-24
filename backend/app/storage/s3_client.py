import os

try:
    import boto3  # type: ignore
except ImportError:  # pragma: no cover - fallback for environments without boto3
    boto3 = None


def get_s3_client():
    """Create an S3 client configured for AWS S3 or MinIO."""
    provider = os.environ.get("STORAGE_PROVIDER", "s3").lower()
    region = os.environ.get("S3_REGION")
    endpoint_url = os.environ.get("S3_ENDPOINT_URL")

    if boto3 is None:
        class _DummyClient:
            def generate_presigned_post(self, Bucket, Key, Fields, Conditions, ExpiresIn):
                url = endpoint_url or f"https://{Bucket}.s3.amazonaws.com/{Key}"
                return {"url": url, "fields": Fields}

        return _DummyClient()

    kwargs = {}
    if region:
        kwargs["region_name"] = region
    if provider == "minio" and endpoint_url:
        kwargs["endpoint_url"] = endpoint_url

    return boto3.client("s3", **kwargs)
