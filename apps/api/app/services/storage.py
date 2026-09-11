"""S3-compatible object storage.

Talks plain S3 so the backend is storage-agnostic: SeaweedFS locally (see
compose.yaml), Garage / R2 / MinIO / S3 in prod — only env vars change.
"""

from functools import lru_cache
from typing import BinaryIO

from minio import Minio
from minio.helpers import ObjectWriteResult

from app.core.config import get_settings


def split_endpoint(endpoint: str) -> tuple[str, bool]:
    """Minio() wants host:port plus a secure flag, not a URL."""
    if endpoint.startswith(("http://", "https://")):
        secure = endpoint.startswith("https://")
        return endpoint.removeprefix("http://").removeprefix("https://"), secure
    return endpoint, True


@lru_cache
def get_s3_client() -> Minio:
    settings = get_settings()
    endpoint, secure = split_endpoint(settings.s3_endpoint)
    return Minio(
        endpoint,
        access_key=settings.s3_access_key,
        secret_key=settings.s3_secret_key,
        secure=secure,
    )


def ensure_bucket(client: Minio | None = None, bucket: str | None = None) -> None:
    settings = get_settings()
    client = client or get_s3_client()
    bucket = bucket or settings.s3_bucket
    if not client.bucket_exists(bucket):
        client.make_bucket(bucket)


def put_object(
    key: str,
    data: BinaryIO,
    length: int,
    content_type: str = "application/octet-stream",
    bucket: str | None = None,
) -> ObjectWriteResult:
    return get_s3_client().put_object(
        bucket or get_settings().s3_bucket,
        key,
        data,
        length,
        content_type=content_type,
    )


def presigned_get(key: str, expires_hours: int = 1, bucket: str | None = None) -> str:
    """Time-limited download URL — hand these to the browser, never bucket keys."""
    from datetime import timedelta

    return get_s3_client().presigned_get_object(
        bucket or get_settings().s3_bucket,
        key,
        expires=timedelta(hours=expires_hours),
    )
