import asyncio
import os
import socket
from typing import AsyncGenerator, Dict

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient


def _get_free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


_GRPC_PORT = str(_get_free_port())
_HTTP_PORT = str(_get_free_port())

os.environ["HOST"] = "127.0.0.1"
os.environ["PORT"] = _HTTP_PORT
os.environ["GRPC_PORT"] = _GRPC_PORT
os.environ["VERSION"] = "test"
os.environ["API_V1_STR"] = "/api/v1"
os.environ["POSTGRES_SERVER"] = "localhost"
os.environ["POSTGRES_PORT"] = "5432"
os.environ["POSTGRES_USER"] = "test_user"
os.environ["POSTGRES_PASSWORD"] = "test_password"
os.environ["POSTGRES_DB"] = "test_db"
os.environ["MESSAGE_BROKERS"] = "test-broker:19092"
os.environ["ADMIN_CONNECTIONS_TOPIC"] = "admin_connections"
os.environ["ADMIN_RESPONSE_TOPIC"] = "admin_responses"
os.environ["MODULES_SERVICE_URL"] = "localhost:50051"
os.environ["MODULES_HEARTBEAT_INTERVAL"] = "0"

from core import config as config_module  # noqa: E402

config_module.settings.HOST = "127.0.0.1"
config_module.settings.PORT = int(_HTTP_PORT)
config_module.settings.GRPC_PORT = int(_GRPC_PORT)
config_module.settings.MESSAGE_BROKERS = "test-broker:19092"
config_module.settings.MODULES_SERVICE_URL = "localhost:50051"
config_module.settings.MODULES_HEARTBEAT_INTERVAL = 0


@pytest.fixture(scope="session")
def grpc_port() -> int:
    return int(_GRPC_PORT)


@pytest.fixture(autouse=True)
def patch_health(monkeypatch):
    from services.health_service import HealthService
    from services.modules_client_manager import set_client

    async def _always_true(self):
        return True

    monkeypatch.setattr(HealthService, "_check_redpanda", _always_true)
    monkeypatch.setattr(HealthService, "_check_modules_service", _always_true)

    class DummyModulesClient:
        is_healthy = True

    set_client(DummyModulesClient())
    yield
    set_client(None)


@pytest_asyncio.fixture
async def database(tmp_path) -> AsyncGenerator:
    from shared.database.utils import DatabaseManager
    from core import database as database_module
    from models.base import Base  # noqa: F401
    from models import connection, image, status, working  # noqa: F401

    db_path = tmp_path / "connections_test.db"
    sqlite_url = f"sqlite+aiosqlite:///{db_path}"

    config_module.settings.DATABASE_URL = sqlite_url

    database_manager = DatabaseManager(sqlite_url)
    database_manager.create_async_engine()
    database_module.db_manager = database_manager

    async with database_manager.engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield database_manager

    await database_manager.close()
    await asyncio.sleep(0)
    if db_path.exists():
        db_path.unlink()


@pytest_asyncio.fixture
async def grpc_server(database, grpc_port: int):
    import grpc
    from generated.connections import connections_pb2_grpc
    from workers.grpc_service import ConnectionsGrpcService

    server = grpc.aio.server()
    connections_pb2_grpc.add_ConnectionsServiceServicer_to_server(
        ConnectionsGrpcService(), server
    )
    listen_addr = f"127.0.0.1:{grpc_port}"
    server.add_insecure_port(listen_addr)
    await server.start()
    try:
        yield server
    finally:
        await server.stop(0)


@pytest_asyncio.fixture
async def grpc_stub(grpc_server, grpc_port: int):
    import grpc
    from generated.connections import connections_pb2_grpc

    channel = grpc.aio.insecure_channel(f"127.0.0.1:{grpc_port}")
    await channel.channel_ready()
    stub = connections_pb2_grpc.ConnectionsServiceStub(channel)
    try:
        yield stub
    finally:
        await channel.close()


@pytest_asyncio.fixture
async def http_client(database):
    from fastapi import FastAPI
    from api.v1.router import api_router
    from core.database import get_db as get_db_dependency

    app = FastAPI()
    app.include_router(api_router, prefix="/api/v1")

    async def override_get_db():
        session = database.async_session()
        try:
            yield session
        finally:
            await session.close()

    app.dependency_overrides[get_db_dependency] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        yield client


@pytest_asyncio.fixture
async def seed_data(database) -> AsyncGenerator[Dict[str, int], None]:
    from sqlalchemy import delete
    from models.connection import ConnectionModel
    from models.image import ImageModel
    from models.status import StatusModel
    from models.working import WorkingModel

    session = database.async_session()
    try:
        await session.execute(delete(ConnectionModel))
        await session.execute(delete(ImageModel))
        await session.execute(delete(StatusModel))
        await session.execute(delete(WorkingModel))
        await session.commit()

        connection = ConnectionModel(
            label="GitHub",
            type="link",
            href="https://github.com",
            value="https://github.com/iizhukov",
        )
        image = ImageModel(
            filename="avatar.png",
            content_type="image/png",
            url="https://cdn.example/avatar.png",
        )
        status = StatusModel(status="active")
        working = WorkingModel(working_on="Open source", percentage=42)

        session.add_all([connection, image, status, working])
        await session.flush()
        ids = {
            "connection_id": connection.id,
            "image_id": image.id,
            "status_id": status.id,
            "working_id": working.id,
        }
        await session.commit()
    finally:
        await session.close()

    yield ids

    session = database.async_session()
    try:
        await session.execute(delete(ConnectionModel))
        await session.execute(delete(ImageModel))
        await session.execute(delete(StatusModel))
        await session.execute(delete(WorkingModel))
        await session.commit()
    finally:
        await session.close()
