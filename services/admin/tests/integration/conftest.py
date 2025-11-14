import base64
import os
import socket
from datetime import datetime, timezone
from typing import Any, Dict, Optional

import pytest


def _get_free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


os.environ.setdefault("HOST", "127.0.0.1")
os.environ.setdefault("PORT", "9100")
os.environ.setdefault("GRPC_PORT", "51000")
os.environ.setdefault("REDPANDA_BROKERS", "redpanda:9092")
os.environ.setdefault("UPLOAD_SERVICE_GRPC_HOST", "upload")
os.environ.setdefault("UPLOAD_SERVICE_GRPC_PORT", "5001")
os.environ.setdefault("MODULES_GRPC_HOST", "modules")
os.environ.setdefault("MODULES_GRPC_PORT", "5002")
os.environ.setdefault("MONGODB_URI", "mongodb://localhost:27017")
os.environ.setdefault("MONGODB_DATABASE", "admin_test")
os.environ.setdefault("ADMIN_RESPONSE_TOPIC", "admin.responses")
os.environ.setdefault("REQUEST_TIMEOUT", "5")

from core import config as config_module  # noqa: E402
from services.message_service import MessageService  # noqa: E402
from scripts.generate_grpc import main as generate_grpc_files  # noqa: E402

try:  # noqa: SIM105
    from generated.admin import admin_pb2  # type: ignore  # noqa: F401
except ImportError:  # pragma: no cover
    generate_grpc_files()

config_module.settings.HOST = "127.0.0.1"
config_module.settings.PORT = 9100
config_module.settings.GRPC_PORT = 51000
config_module.settings.REDPANDA_BROKERS = "redpanda:9092"
config_module.settings.UPLOAD_SERVICE_GRPC_HOST = "upload"
config_module.settings.UPLOAD_SERVICE_GRPC_PORT = 5001
config_module.settings.MODULES_GRPC_HOST = "modules"
config_module.settings.MODULES_GRPC_PORT = 5002
config_module.settings.MONGODB_URI = "mongodb://localhost:27017"
config_module.settings.MONGODB_DATABASE = "admin_test"
config_module.settings.ADMIN_RESPONSE_TOPIC = "admin.responses"


class FakeMessageRepository:
    def __init__(self) -> None:
        self.records: Dict[str, Dict[str, Any]] = {}

    async def create_message(
        self,
        request_id: str,
        service: str,
        payload: Dict[str, Any],
        file_info: Optional[Dict[str, Any]],
    ) -> Dict[str, Any]:
        now = datetime.now(timezone.utc)
        record = {
            "request_id": request_id,
            "service": service,
            "payload": payload,
            "file": file_info,
            "status": "pending",
            "response": None,
            "created_at": now,
            "updated_at": now,
        }
        self.records[request_id] = record
        return record

    async def mark_failed(self, request_id: str, error: str) -> None:
        record = self.records.get(request_id)
        if record:
            record["status"] = "error"
            record["response"] = {"error": error}
            record["updated_at"] = datetime.now(timezone.utc)

    async def apply_response(
        self,
        request_id: str,
        status: str,
        response: Optional[Dict[str, Any]],
    ) -> Optional[Dict[str, Any]]:
        record = self.records.get(request_id)
        if record:
            record["status"] = status
            record["response"] = response
            record["updated_at"] = datetime.now(timezone.utc)
            return record
        return None

    async def get_message(self, request_id: str) -> Optional[Dict[str, Any]]:
        return self.records.get(request_id)


class FakeUploadClient:
    def __init__(self) -> None:
        self.uploads: list[Dict[str, Any]] = []

    async def upload(
        self,
        service: str,
        file_payload,
    ) -> Dict[str, Any]:
        size = len(base64.b64decode(file_payload.content.encode()))
        info = {
            "filename": f"{service}/{file_payload.full_name}",
            "content_type": "application/octet-stream",
            "url": f"https://files/{service}/{file_payload.full_name}",
            "bucket": "test",
            "size": size,
        }
        self.uploads.append({"service": service, "payload": file_payload, "info": info})
        return info

    async def close(self) -> None:
        pass


class FakeModulesClient:
    def __init__(self, topics: Optional[Dict[str, str]] = None) -> None:
        self.topics = topics or {}

    async def get_admin_topic(self, service_name: str) -> Optional[str]:
        return self.topics.get(service_name)

    async def close(self) -> None:
        pass


class FakeKafkaManager:
    def __init__(self) -> None:
        self.messages: list[tuple[str, Dict[str, Any]]] = []
        self.handlers: list[Any] = []

    async def send(self, topic: str, message: Dict[str, Any]) -> None:
        self.messages.append((topic, message))

    async def start_response_listener(self, handler) -> None:
        self.handlers.append(handler)

    async def close(self) -> None:
        pass


@pytest.fixture
def service_components() -> Dict[str, Any]:
    repository = FakeMessageRepository()
    upload_client = FakeUploadClient()
    modules_client = FakeModulesClient({"connections": "admin.connections"})
    kafka_manager = FakeKafkaManager()
    service = MessageService(
        repository=repository,
        upload_client=upload_client,
        modules_client=modules_client,
        kafka_manager=kafka_manager,
    )
    return {
        "service": service,
        "repository": repository,
        "upload": upload_client,
        "modules": modules_client,
        "kafka": kafka_manager,
    }



