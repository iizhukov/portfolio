import os
import sys
from pathlib import Path
from typing import Any, Dict, Optional

import grpc
import pytest
import pytest_asyncio
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

ENV_DEFAULTS = {
    "HOST": "127.0.0.1",
    "PORT": "9400",
    "VERSION": "1.0.0",
    "API_V1_STR": "/api/v1",
    "CONNECTIONS_SERVICE_HOST": "connections.test",
    "CONNECTIONS_SERVICE_PORT": "50051",
    "PROJECTS_SERVICE_HOST": "projects.test",
    "PROJECTS_SERVICE_PORT": "50052",
    "MODULES_SERVICE_HOST": "modules.test",
    "MODULES_SERVICE_PORT": "50053",
    "MODULES_HTTP_PORT": "9500",
    "ADMIN_SERVICE_HOST": "admin.test",
    "ADMIN_SERVICE_PORT": "50054",
    "ADMIN_HTTP_PORT": "9600",
    "UPLOAD_SERVICE_HOST": "upload.test",
    "UPLOAD_SERVICE_PORT": "50055",
    "REDIS_HOST": "redis.test",
    "REDIS_PORT": "6379",
    "REDIS_DB": "0",
    "REDIS_PASSWORD": "",
    "GRPC_TIMEOUT": "5",
    "GRPC_MAX_RETRIES": "3",
    "CACHE_TTL_DEFAULT": "120",
    "CACHE_TTL_CONNECTIONS": "60",
    "CACHE_TTL_MODULES": "180",
    "CACHE_TTL_ADMIN": "60",
    "LOG_LEVEL": "INFO",
}

for key, value in ENV_DEFAULTS.items():
    os.environ.setdefault(key, value)

SERVICE_ROOT = Path(__file__).resolve().parents[2]
if str(SERVICE_ROOT) not in sys.path:
    sys.path.insert(0, str(SERVICE_ROOT))

from scripts.generate_grpc import main as generate_grpc_files  # noqa: E402

try:  # noqa: SIM105
    from generated import projects as _projects_pkg  # type: ignore  # noqa: F401
except ImportError:  # pragma: no cover
    generate_grpc_files()

from generated.projects import projects_pb2  # noqa: E402
from generated.connections import connections_pb2  # noqa: E402
from generated.modules import modules_pb2  # noqa: E402
from generated.admin import admin_pb2  # noqa: E402

from core import config as config_module  # noqa: E402
from services import dependencies as dependencies_module  # noqa: E402
from services.redis_manager import RedisManager  # noqa: E402
from services.grpc_client_manager import GrpcClientManager  # noqa: E402
from services.admin_client import AdminClient  # noqa: E402

settings = config_module.settings
settings.HOST = "127.0.0.1"
settings.PORT = 9400
settings.VERSION = "1.0.0"
settings.API_V1_STR = "/api/v1"
settings.CONNECTIONS_SERVICE_HOST = "connections.test"
settings.CONNECTIONS_SERVICE_PORT = 50051
settings.PROJECTS_SERVICE_HOST = "projects.test"
settings.PROJECTS_SERVICE_PORT = 50052
settings.MODULES_SERVICE_HOST = "modules.test"
settings.MODULES_SERVICE_PORT = 50053
settings.MODULES_HTTP_PORT = 9500
settings.ADMIN_SERVICE_HOST = "admin.test"
settings.ADMIN_SERVICE_PORT = 50054
settings.ADMIN_HTTP_PORT = 9600
settings.UPLOAD_SERVICE_HOST = "upload.test"
settings.UPLOAD_SERVICE_PORT = 50055
settings.REDIS_HOST = "redis.test"
settings.REDIS_PORT = 6379
settings.REDIS_DB = 0
settings.REDIS_PASSWORD = ""
settings.REDIS_URL = "redis://redis.test:6379/0"
settings.GRPC_TIMEOUT = 5
settings.GRPC_MAX_RETRIES = 3
settings.CACHE_TTL_DEFAULT = 120
settings.CACHE_TTL_CONNECTIONS = 60
settings.CACHE_TTL_MODULES = 180
settings.CACHE_TTL_ADMIN = 60
settings.LOG_LEVEL = "INFO"


class FakeProjectsClient:
    def __init__(self) -> None:
        child = projects_pb2.Project(
            id=2,
            name="Docs",
            type="file",
            file_type="markdown",
            parent_id=1,
            url="https://cdn.example/docs.md",
            created_at="2024-01-02T00:00:00Z",
            updated_at="2024-01-02T00:00:00Z",
        )
        root = projects_pb2.Project(
            id=1,
            name="Root",
            type="folder",
            children=[child],
            created_at="2024-01-01T00:00:00Z",
            updated_at="2024-01-01T00:00:00Z",
        )
        self.projects_response = projects_pb2.GetProjectsResponse(projects=[root])
        self.project_tree_response = projects_pb2.GetProjectTreeResponse(projects=[root])
        self.project_by_id_response = projects_pb2.GetProjectByIdResponse(project=root)
        self.health_response = projects_pb2.HealthCheckResponse(
            status="ok",
            timestamp="2024-01-01T00:00:00Z",
            database=True,
            redpanda=True,
            modules_service=True,
        )
        self.last_parent_id: Optional[int] = None
        self.last_root_id: Optional[int] = None

    async def GetProjects(self, request, timeout: Optional[int] = None):
        del timeout
        self.last_parent_id = request.parent_id if request.HasField("parent_id") else None
        return self.projects_response

    async def GetProjectById(self, request, timeout: Optional[int] = None):
        del timeout
        return self.project_by_id_response

    async def GetProjectTree(self, request, timeout: Optional[int] = None):
        del timeout
        self.last_root_id = request.root_id if request.HasField("root_id") else None
        return self.project_tree_response

    async def HealthCheck(self, request, timeout: Optional[int] = None):
        del request, timeout
        return self.health_response


class FakeConnectionsClient:
    def __init__(self) -> None:
        self.connections_response = connections_pb2.GetConnectionsResponse(
            connections=[
                connections_pb2.Connection(
                    id=1,
                    label="GitHub",
                    type="social",
                    href="https://github.com/iizhukov",
                    value="@iizhukov",
                )
            ]
        )
        self.image_response = connections_pb2.GetImageResponse(
            image=connections_pb2.Image(
                id=5,
                filename="avatar.png",
                content_type="image/png",
                url="https://cdn.example/avatar.png",
            )
        )
        self.status_response = connections_pb2.GetStatusResponse(
            status=connections_pb2.Status(id=3, status="active")
        )
        self.working_response = connections_pb2.GetWorkingResponse(
            working=connections_pb2.Working(id=7, working_on="Gateway", percentage=80)
        )
        self.health_response = connections_pb2.HealthCheckResponse(
            status="healthy",
            timestamp="2024-01-01T00:00:00Z",
            database=True,
            redpanda=True,
            modules_service=True,
        )

    async def GetConnections(self, request, timeout: Optional[int] = None):
        del request, timeout
        return self.connections_response

    async def GetImage(self, request, timeout: Optional[int] = None):
        del request, timeout
        return self.image_response

    async def GetStatus(self, request, timeout: Optional[int] = None):
        del request, timeout
        return self.status_response

    async def GetWorking(self, request, timeout: Optional[int] = None):
        del request, timeout
        return self.working_response

    async def HealthCheck(self, request, timeout: Optional[int] = None):
        del request, timeout
        return self.health_response


class FakeModulesClient:
    def __init__(self) -> None:
        service = modules_pb2.ServiceInfo(
            id=10,
            service_name="connections",
            version="1.0.0",
            admin_topic="admin.connections",
            ttl_seconds=30,
            status="online",
            created_at="2024-01-01T00:00:00Z",
            updated_at="2024-01-01T00:00:00Z",
        )
        self.services: Dict[str, modules_pb2.ServiceInfo] = {
            service.service_name: service,
        }
        self.raise_for_service: Dict[str, Exception] = {}

    async def ListServices(self, request, timeout: Optional[int] = None):
        del request, timeout
        return modules_pb2.ListServicesResponse(services=list(self.services.values()))

    async def GetService(self, request, timeout: Optional[int] = None):
        del timeout
        if request.service_name in self.raise_for_service:
            raise self.raise_for_service[request.service_name]
        service = self.services.get(request.service_name)
        if not service:
            raise FakeRpcError(grpc.StatusCode.NOT_FOUND, "Service not found")
        return modules_pb2.GetServiceResponse(service=service)


class FakeGrpcClientManager(GrpcClientManager):  # type: ignore[misc]
    def __init__(
        self,
        projects_client: FakeProjectsClient,
        connections_client: FakeConnectionsClient,
        modules_client: FakeModulesClient,
    ) -> None:
        super().__init__()
        self.projects_client = projects_client
        self.connections_client = connections_client
        self.modules_client = modules_client

    async def initialize(self):
        return

    async def get_client(self, service_name: str):
        mapping = {
            "projects": self.projects_client,
            "connections": self.connections_client,
            "modules": self.modules_client,
        }
        if service_name not in mapping:
            raise ValueError(f"Service '{service_name}' not found")
        return mapping[service_name]

    async def call_grpc_with_retry(self, client, method, request, timeout=30):  # noqa: D401
        del client
        return await method(request, timeout=timeout)

    async def close(self):
        return


class FakeAdminClient(AdminClient):  # type: ignore[misc]
    def __init__(self) -> None:
        super().__init__()
        self.submit_response: Dict[str, Any] = {
            "request_id": "req-1",
            "status": "pending",
            "service": "connections",
            "payload": {"action": "restart"},
            "file": None,
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-01T00:00:00Z",
        }
        self.messages: Dict[str, Dict[str, Any]] = {}
        self.last_payload: Optional[Dict[str, Any]] = None
        self.raise_for_submit: Optional[Exception] = None
        self.raise_for_get: Optional[Exception] = None

    async def initialize(self):
        return

    async def close(self):
        return

    async def submit_command(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        if self.raise_for_submit:
            raise self.raise_for_submit
        self.last_payload = payload
        return self.submit_response

    async def get_message(self, request_id: str) -> Dict[str, Any]:
        if self.raise_for_get:
            raise self.raise_for_get
        if request_id not in self.messages:
            raise FakeRpcError(grpc.StatusCode.NOT_FOUND, "Message not found")
        return self.messages[request_id]


class FakeRedisManager(RedisManager):  # type: ignore[misc]
    def __init__(self) -> None:
        super().__init__()
        self._initialized = True
        self.store: Dict[str, Any] = {}

    async def initialize(self):
        self._initialized = True

    async def close(self):
        self._initialized = False

    async def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None):
        del params
        return self.store.get(endpoint)

    async def set(self, endpoint: str, data: Any, ttl: int, params: Optional[Dict[str, Any]] = None):
        del params, ttl
        self.store[endpoint] = data

    async def delete(self, endpoint: str, params: Optional[Dict[str, Any]] = None):
        del params
        self.store.pop(endpoint, None)

    async def delete_pattern(self, pattern: str):
        to_delete = [key for key in self.store if pattern in key]
        for key in to_delete:
            self.store.pop(key, None)

    async def get_ttl_for_endpoint(self, endpoint: str) -> int:
        if endpoint.startswith("/api/v1/connections"):
            return settings.CACHE_TTL_CONNECTIONS
        if endpoint.startswith("/api/v1/modules"):
            return settings.CACHE_TTL_MODULES
        if endpoint.startswith("/api/v1/admin"):
            return settings.CACHE_TTL_ADMIN
        return settings.CACHE_TTL_DEFAULT


class FakeRpcError(grpc.RpcError):
    def __init__(self, status_code: grpc.StatusCode, message: str):
        super().__init__()
        self._status_code = status_code
        self._message = message

    def code(self):
        return self._status_code

    def details(self):
        return self._message


@pytest.fixture
def fake_projects_client() -> FakeProjectsClient:
    return FakeProjectsClient()


@pytest.fixture
def fake_connections_client() -> FakeConnectionsClient:
    return FakeConnectionsClient()


@pytest.fixture
def fake_modules_client() -> FakeModulesClient:
    return FakeModulesClient()


@pytest.fixture
def fake_grpc_manager(
    fake_projects_client: FakeProjectsClient,
    fake_connections_client: FakeConnectionsClient,
    fake_modules_client: FakeModulesClient,
) -> FakeGrpcClientManager:
    return FakeGrpcClientManager(
        projects_client=fake_projects_client,
        connections_client=fake_connections_client,
        modules_client=fake_modules_client,
    )


@pytest.fixture
def fake_admin_client() -> FakeAdminClient:
    return FakeAdminClient()


@pytest.fixture
def fake_redis_manager() -> FakeRedisManager:
    return FakeRedisManager()


@pytest.fixture
def app(fake_grpc_manager, fake_admin_client, fake_redis_manager):
    from api.v1.api import api_router
    from services.dependencies import (
        get_admin_client,
        get_grpc_manager,
        get_redis_manager,
    )

    original_grpc = dependencies_module._grpc_manager
    original_admin = dependencies_module._admin_client
    original_redis = dependencies_module._redis_manager

    dependencies_module._grpc_manager = fake_grpc_manager
    dependencies_module._admin_client = fake_admin_client
    dependencies_module._redis_manager = fake_redis_manager

    app = FastAPI()
    app.include_router(api_router, prefix="/api/v1")

    app.dependency_overrides[get_grpc_manager] = lambda: fake_grpc_manager
    app.dependency_overrides[get_admin_client] = lambda: fake_admin_client
    app.dependency_overrides[get_redis_manager] = lambda: fake_redis_manager

    try:
        yield app
    finally:
        app.dependency_overrides.clear()
        dependencies_module._grpc_manager = original_grpc
        dependencies_module._admin_client = original_admin
        dependencies_module._redis_manager = original_redis


@pytest_asyncio.fixture
async def client(app):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as http_client:
        yield http_client

