import asyncio
import contextlib
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
os.environ["ADMIN_PROJECTS_TOPIC"] = "admin_projects"
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


@pytest_asyncio.fixture
async def database(tmp_path) -> AsyncGenerator:
    from shared.database.utils import DatabaseManager
    from core import database as database_module
    from models.base import Base  # noqa: F401
    from models import project  # noqa: F401

    db_path = tmp_path / "projects_test.db"
    sqlite_url = f"sqlite+aiosqlite:///{db_path}"

    config_module.settings.DATABASE_URL = sqlite_url

    database_manager = DatabaseManager(sqlite_url)
    database_manager.create_async_engine()

    database_module.db_manager = database_manager

    async with database_manager.engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield database_manager

    await database_manager.close()
    if db_path.exists():
        db_path.unlink()


@pytest_asyncio.fixture
async def grpc_server(database, grpc_port: int):
    import grpc
    from generated.projects import projects_pb2_grpc
    from workers.grpc_service import ProjectsGrpcService

    server = grpc.aio.server()
    projects_pb2_grpc.add_ProjectsServiceServicer_to_server(
        ProjectsGrpcService(), server
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

    from generated.projects import projects_pb2_grpc

    channel = grpc.aio.insecure_channel(f"127.0.0.1:{grpc_port}")
    await channel.channel_ready()
    stub = projects_pb2_grpc.ProjectsServiceStub(channel)
    try:
        yield stub
    finally:
        await channel.close()


@pytest_asyncio.fixture
async def http_client():
    from fastapi import FastAPI
    from api.v1.router import api_router

    app = FastAPI()
    app.include_router(api_router, prefix="/api/v1")

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        yield client


@pytest_asyncio.fixture
async def seed_projects(database) -> AsyncGenerator[Dict[str, int], None]:
    from sqlalchemy import delete
    from models.project import ProjectModel

    async with database.async_session() as session:
        await session.execute(delete(ProjectModel))
        await session.commit()

        root = ProjectModel(
            name="Root Project",
            type="folder",
            file_type=None,
            parent_id=None,
            url=None,
        )
        child = ProjectModel(
            name="Child Project",
            type="file",
            file_type="readme",
            parent=root,
            url="https://example.com/readme",
        )

        session.add_all([root, child])
        await session.flush()
        ids = {"root_id": root.id, "child_id": child.id}
        await session.commit()

    yield ids

    async with database.async_session() as session:
        await session.execute(delete(ProjectModel))
        await session.commit()


