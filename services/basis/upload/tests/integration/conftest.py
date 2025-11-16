import os
from threading import Lock
from typing import Any, Dict, Optional

import pytest

os.environ.setdefault("HOST", "127.0.0.1")
os.environ.setdefault("PORT", "9200")
os.environ.setdefault("GRPC_PORT", "52000")
os.environ.setdefault("MINIO_ENDPOINT", "minio.test:9000")
os.environ.setdefault("MINIO_ACCESS_KEY", "test-access")
os.environ.setdefault("MINIO_SECRET_KEY", "test-secret")
os.environ.setdefault("MINIO_BUCKET", "test-bucket")
os.environ.setdefault("MINIO_REGION", "")
os.environ.setdefault("MINIO_EXTERNAL_URL", "http://cdn.minio.test")

from scripts.generate_grpc import main as generate_grpc_files  # noqa: E402

try:  # noqa: SIM105
    from generated.upload import upload_pb2  # type: ignore  # noqa: F401
except ImportError:  # pragma: no cover
    generate_grpc_files()

from core import config as config_module  # noqa: E402
from services.storage_service import StorageService  # noqa: E402
from services import dependencies as dependencies_module  # noqa: E402

settings = config_module.settings
settings.HOST = "127.0.0.1"
settings.PORT = 9200
settings.GRPC_PORT = 52000
settings.MINIO_ENDPOINT = "minio.test:9000"
settings.MINIO_ACCESS_KEY = "test-access"
settings.MINIO_SECRET_KEY = "test-secret"
settings.MINIO_BUCKET = "test-bucket"
settings.MINIO_REGION = ""
settings.MINIO_SECURE = False
settings.MINIO_EXTERNAL_URL = "http://cdn.minio.test"


class FakeMinio:
    def __init__(self) -> None:
        self._lock = Lock()
        self.buckets: set[str] = set()
        self.objects: Dict[tuple[str, str], Dict[str, Any]] = {}

    def bucket_exists(self, bucket: str) -> bool:
        with self._lock:
            return bucket in self.buckets

    def make_bucket(self, bucket: str, location: Optional[str] = None) -> None:
        del location
        with self._lock:
            self.buckets.add(bucket)

    def put_object(
        self,
        bucket: str,
        object_name: str,
        data_stream,
        length: int,
        content_type: Optional[str],
    ) -> None:
        data = data_stream.read(length)
        with self._lock:
            self.objects[(bucket, object_name)] = {
                "data": data,
                "length": length,
                "content_type": content_type,
            }

    def list_buckets(self) -> list[str]:
        with self._lock:
            return list(self.buckets)


@pytest.fixture(autouse=True)
def reset_dependency_singleton():
    original = dependencies_module._storage_service
    dependencies_module._storage_service = None
    try:
        yield
    finally:
        dependencies_module._storage_service = original


@pytest.fixture
def fake_minio() -> FakeMinio:
    return FakeMinio()


@pytest.fixture
def storage_service(fake_minio: FakeMinio) -> StorageService:
    return StorageService(fake_minio)
