from __future__ import annotations

from minio import Minio

from core.config import settings


def create_minio_client() -> Minio:
    endpoint = settings.MINIO_ENDPOINT
    access_key = settings.MINIO_ACCESS_KEY
    secret_key = settings.MINIO_SECRET_KEY
    secure = settings.MINIO_SECURE

    return Minio(
        endpoint,
        access_key=access_key,
        secret_key=secret_key,
        secure=secure,
        region=settings.MINIO_REGION or None,
    )
