from typing import Optional

from core.minio_client import create_minio_client
from services.storage_service import StorageService


_storage_service: Optional[StorageService] = None


def get_storage_service() -> StorageService:
    global _storage_service
    if _storage_service is None:
        client = create_minio_client()
        _storage_service = StorageService(client)
    return _storage_service
