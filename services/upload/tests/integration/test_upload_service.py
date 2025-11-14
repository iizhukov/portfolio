import socket
from typing import Tuple

import grpc
import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from api.v1.router import router as api_router
from core.config import settings
from generated.upload import upload_pb2, upload_pb2_grpc
from schemas.upload import UploadResponse
from services.dependencies import get_storage_service
from services.storage_service import StorageService
from workers.grpc_service import UploadGrpcService


pytestmark = pytest.mark.asyncio


def _get_free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


async def _create_grpc_stub(storage: StorageService) -> Tuple[upload_pb2_grpc.UploadServiceStub, grpc.aio.Server, grpc.aio.Channel]:
    port = _get_free_port()
    server = grpc.aio.server()
    upload_pb2_grpc.add_UploadServiceServicer_to_server(
        UploadGrpcService(storage),
        server,
    )
    listen_addr = f"127.0.0.1:{port}"
    server.add_insecure_port(listen_addr)
    await server.start()

    channel = grpc.aio.insecure_channel(listen_addr)
    await channel.channel_ready()
    stub = upload_pb2_grpc.UploadServiceStub(channel)
    return stub, server, channel


async def _create_http_client(storage: StorageService) -> Tuple[FastAPI, AsyncClient]:
    app = FastAPI()
    app.include_router(api_router, prefix="/api/v1")
    app.dependency_overrides[get_storage_service] = lambda: storage
    transport = ASGITransport(app=app)
    client = AsyncClient(transport=transport, base_url="http://testserver")
    return app, client


async def test_grpc_upload_file_success(storage_service: StorageService):
    stub, server, channel = await _create_grpc_stub(storage_service)
    try:
        request = upload_pb2.UploadRequest(
            folder="projects",
            filename="diagram.png",
            content=b"binary-data",
            content_type="image/png",
        )

        response = await stub.UploadFile(request)

        assert response.bucket == settings.MINIO_BUCKET
        assert response.object_name == "projects/diagram.png"
        assert response.content_type == "image/png"
        assert response.size == len(request.content)

        stored = storage_service.client.objects[(settings.MINIO_BUCKET, "projects/diagram.png")]
        assert stored["data"] == b"binary-data"
        assert stored["content_type"] == "image/png"
    finally:
        await channel.close()
        await server.stop(0)


async def test_grpc_upload_generates_name_when_missing(storage_service: StorageService):
    stub, server, channel = await _create_grpc_stub(storage_service)
    try:
        request = upload_pb2.UploadRequest(
            folder="",
            filename="",
            content=b"log entry",
            content_type="",
        )

        response = await stub.UploadFile(request)

        assert response.bucket == settings.MINIO_BUCKET
        assert response.object_name
        stored = storage_service.client.objects[(settings.MINIO_BUCKET, response.object_name)]
        assert stored["data"] == b"log entry"
        assert stored["content_type"] == "application/octet-stream"
        assert response.url.endswith(response.object_name)
    finally:
        await channel.close()
        await server.stop(0)


async def test_http_upload_file_success(storage_service: StorageService):
    app, client = await _create_http_client(storage_service)
    try:
        files = {"file": ("report.txt", b"hello http", "text/plain")}
        data = {"folder": "reports", "filename": "daily.txt"}

        response = await client.post("/api/v1/upload", data=data, files=files)

        assert response.status_code == 201
        payload = UploadResponse(**response.json())
        assert payload.bucket == settings.MINIO_BUCKET
        assert payload.object_name == "reports/daily.txt"
        stored = storage_service.client.objects[(settings.MINIO_BUCKET, "reports/daily.txt")]
        assert stored["data"] == b"hello http"
        assert stored["content_type"] == "text/plain"
    finally:
        await client.aclose()
        app.dependency_overrides.clear()


async def test_http_upload_file_failure_returns_500(storage_service: StorageService, monkeypatch: pytest.MonkeyPatch):
    async def failing_upload(*args, **kwargs):  # noqa: ANN001, ANN002
        raise RuntimeError("boom")

    monkeypatch.setattr(storage_service, "upload_file", failing_upload)

    app, client = await _create_http_client(storage_service)
    try:
        files = {"file": ("any.bin", b"boom", "application/octet-stream")}
        data = {"folder": "failures"}

        response = await client.post("/api/v1/upload", data=data, files=files)

        assert response.status_code == 500
        assert response.json() == {"detail": "Failed to upload file"}
    finally:
        await client.aclose()
        app.dependency_overrides.clear()

