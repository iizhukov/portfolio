import asyncio
import os
import socket
from datetime import datetime, timezone
from typing import AsyncGenerator

import pytest
import pytest_asyncio
import sqlite3


def _get_free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


_GRPC_PORT = str(_get_free_port())

os.environ["HOST"] = "127.0.0.1"
os.environ["PORT"] = "9000"
os.environ["GRPC_PORT"] = _GRPC_PORT
os.environ["POSTGRES_SERVER"] = "localhost"
os.environ["POSTGRES_PORT"] = "5432"
os.environ["POSTGRES_USER"] = "test_user"
os.environ["POSTGRES_PASSWORD"] = "test_password"
os.environ["POSTGRES_DB"] = "test_db_modules"
os.environ["MODULES_DEFAULT_TTL"] = "30"

from core import config as config_module  # noqa: E402

config_module.settings.HOST = "127.0.0.1"
config_module.settings.PORT = 9000
config_module.settings.GRPC_PORT = int(_GRPC_PORT)
config_module.settings.POSTGRES_SERVER = "localhost"
config_module.settings.POSTGRES_PORT = "5432"
config_module.settings.POSTGRES_USER = "test_user"
config_module.settings.POSTGRES_PASSWORD = "test_password"
config_module.settings.POSTGRES_DB = "test_db_modules"
config_module.settings.DATABASE_URL = "sqlite+aiosqlite:///:memory:"

sqlite3.register_adapter(datetime, lambda dt: dt.isoformat())


@pytest.fixture(scope="session")
def grpc_port() -> int:
    return int(_GRPC_PORT)


@pytest.fixture(autouse=True)
def patch_registry_now(monkeypatch):
    from services.registry import ServiceRegistry

    def _naive_utc() -> datetime:
        return datetime.now(timezone.utc).replace(tzinfo=None)

    monkeypatch.setattr(
        ServiceRegistry,
        "_now",
        staticmethod(_naive_utc),
    )
    yield


@pytest_asyncio.fixture
async def database(tmp_path) -> AsyncGenerator:
    from shared.database.utils import DatabaseManager
    from core import database as database_module
    from models.base import Base  # noqa: F401
    from models import services  # noqa: F401
    from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
    from sqlalchemy.orm import sessionmaker
    from sqlalchemy.pool import StaticPool

    sqlite_url = "sqlite+aiosqlite:///:memory:"

    config_module.settings.DATABASE_URL = sqlite_url

    database_manager = DatabaseManager(sqlite_url)
    engine = create_async_engine(
        sqlite_url,
        echo=False,
        pool_pre_ping=True,
        poolclass=StaticPool,
    )
    database_manager.engine = engine
    database_manager.async_session = sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    database_module.db_manager = database_manager
    from services import registry as registry_module
    registry_module.db_manager = database_manager

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield database_manager

    await database_manager.close()
    await asyncio.sleep(0)


@pytest_asyncio.fixture
async def grpc_server(database, grpc_port: int):
    import grpc
    from generated.modules import modules_pb2_grpc
    from workers.grpc_service import ModulesGrpcService

    server = grpc.aio.server()
    modules_pb2_grpc.add_ModulesServiceServicer_to_server(
        ModulesGrpcService(), server
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
    from generated.modules import modules_pb2_grpc

    channel = grpc.aio.insecure_channel(f"127.0.0.1:{grpc_port}")
    await channel.channel_ready()
    stub = modules_pb2_grpc.ModulesServiceStub(channel)
    try:
        yield stub
    finally:
        await channel.close()


