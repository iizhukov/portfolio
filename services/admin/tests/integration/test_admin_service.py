import base64
import socket
from datetime import datetime, timezone, timedelta

import grpc
import pytest
from fastapi import FastAPI
from google.protobuf import struct_pb2
from httpx import ASGITransport, AsyncClient

from generated.admin import admin_pb2, admin_pb2_grpc
from schemas.request import AdminCommandRequest
from workers.grpc_service import AdminGrpcService
from api.v1.router import router as api_router
from api.v1.endpoints.admin import get_message_service
import main as admin_main

pytestmark = pytest.mark.asyncio


def _get_free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


async def _create_grpc_stub(message_service):
    port = _get_free_port()
    server = grpc.aio.server()
    admin_pb2_grpc.add_AdminServiceServicer_to_server(
        AdminGrpcService(message_service), server
    )
    listen_addr = f"127.0.0.1:{port}"
    server.add_insecure_port(listen_addr)
    await server.start()

    channel = grpc.aio.insecure_channel(listen_addr)
    await channel.channel_ready()
    stub = admin_pb2_grpc.AdminServiceStub(channel)
    return stub, server, channel


async def _create_http_client(message_service):
    app = FastAPI()
    app.include_router(api_router, prefix="/api/v1")
    app.dependency_overrides[get_message_service] = lambda: message_service

    original_service = admin_main.message_service
    admin_main.message_service = message_service

    transport = ASGITransport(app=app)
    client = AsyncClient(transport=transport, base_url="http://testserver")
    return app, client, original_service


async def test_submit_command_grpc_success(service_components):
    stub, server, channel = await _create_grpc_stub(service_components["service"])
    try:
        struct = struct_pb2.Struct()
        struct.update({"action": "restart"})

        response = await stub.SubmitCommand(
            admin_pb2.SubmitCommandRequest(
                service="connections",
                payload=struct,
            )
        )

        assert response.request_id
        repo = service_components["repository"]
        record = await repo.get_message(response.request_id)
        assert record is not None
        assert record["payload"]["action"] == "restart"

        kafka_manager = service_components["kafka"]
        assert kafka_manager.messages[0][0] == "admin.connections"
    finally:
        await channel.close()
        await server.stop(0)


async def test_submit_command_grpc_with_file_upload(service_components):
    stub, server, channel = await _create_grpc_stub(service_components["service"])
    try:
        content = b"hello admin"
        struct = struct_pb2.Struct()
        struct.update({"action": "deploy"})

        response = await stub.SubmitCommand(
            admin_pb2.SubmitCommandRequest(
                service="connections",
                payload=struct,
                file=admin_pb2.FilePayload(
                    name="report",
                    extension="txt",
                    path="logs",
                    content=content,
                ),
            )
        )

        upload_client = service_components["upload"]
        assert upload_client.uploads
        uploaded = upload_client.uploads[0]["info"]
        assert uploaded["filename"].endswith("report.txt")
        assert uploaded["size"] == len(content)

        repo = service_components["repository"]
        record = await repo.get_message(response.request_id)
        assert record is not None
        assert record["file"] == uploaded
    finally:
        await channel.close()
        await server.stop(0)


async def test_submit_command_unavailable_service_grpc(service_components):
    stub, server, channel = await _create_grpc_stub(service_components["service"])
    service_components["modules"].topics = {}

    try:
        struct = struct_pb2.Struct()
        struct.update({"action": "restart"})

        with pytest.raises(grpc.aio.AioRpcError) as exc:
            await stub.SubmitCommand(
                admin_pb2.SubmitCommandRequest(
                    service="unknown",
                    payload=struct,
                )
            )

        assert exc.value.code() == grpc.StatusCode.UNAVAILABLE
    finally:
        await channel.close()
        await server.stop(0)


async def test_get_message_status_grpc(service_components):
    stub, server, channel = await _create_grpc_stub(service_components["service"])
    request_id = "req-123"
    repo = service_components["repository"]
    await repo.create_message(
        request_id=request_id,
        service="connections",
        payload={"action": "ping"},
        file_info=None,
    )

    try:
        response = await stub.GetMessageStatus(
            admin_pb2.GetMessageStatusRequest(request_id=request_id)
        )

        assert response.request_id == request_id
        assert response.status == "pending"
        assert response.payload["action"] == "ping"
    finally:
        await channel.close()
        await server.stop(0)


async def test_get_message_status_not_found_grpc(service_components):
    stub, server, channel = await _create_grpc_stub(service_components["service"])
    try:
        with pytest.raises(grpc.aio.AioRpcError) as exc:
            await stub.GetMessageStatus(
                admin_pb2.GetMessageStatusRequest(request_id="missing")
            )

        assert exc.value.code() == grpc.StatusCode.NOT_FOUND
    finally:
        await channel.close()
        await server.stop(0)


async def test_handle_response_updates_repository(service_components):
    message_service = service_components["service"]

    command = AdminCommandRequest(service="connections", payload={"action": "status"})
    result = await message_service.submit_command(command)

    await message_service.handle_response(
        {
            "request_id": result.request_id,
            "service": "connections",
            "status": "completed",
            "response": {"ok": True},
        }
    )

    repo = service_components["repository"]
    stored = await repo.get_message(result.request_id)
    assert stored is not None
    assert stored["status"] == "completed"
    assert stored["response"] == {"ok": True}


async def test_http_submit_command_success(service_components):
    app, client, original_service = await _create_http_client(service_components["service"])
    async with client:
        response = await client.post(
                "/api/v1/admin/commands",
            json={"service": "connections", "payload": {"action": "deploy"}},
        )

        assert response.status_code == 202
        data = response.json()
        repo = service_components["repository"]
        record = await repo.get_message(data["request_id"])
        assert record is not None
        assert record["payload"]["action"] == "deploy"
    app.dependency_overrides.clear()
    admin_main.message_service = original_service


async def test_http_submit_command_service_unavailable(service_components):
    service_components["modules"].topics = {}
    app, client, original_service = await _create_http_client(service_components["service"])
    async with client:
        response = await client.post(
            "/api/v1/admin/commands",
            json={"service": "unknown", "payload": {"action": "noop"}},
        )

        assert response.status_code == 503
    app.dependency_overrides.clear()
    admin_main.message_service = original_service


async def test_http_get_message_status(service_components):
    app, client, original_service = await _create_http_client(service_components["service"])
    repo = service_components["repository"]
    request_id = "http-1"
    await repo.create_message(
        request_id=request_id,
        service="connections",
        payload={"action": "info"},
        file_info={"filename": "connections/info.txt"},
    )

    await repo.apply_response(
        request_id=request_id,
        status="completed",
        response={"ok": True},
    )

    async with client:
        response = await client.get(f"/api/v1/admin/messages/{request_id}")
        assert response.status_code == 200
        payload = response.json()
        assert payload["status"] == "completed"
        assert payload["response"] == {"ok": True}
        assert payload["file"]["filename"] == "connections/info.txt"
    app.dependency_overrides.clear()
    admin_main.message_service = original_service


async def test_http_get_message_status_not_found(service_components):
    app, client, original_service = await _create_http_client(service_components["service"])
    async with client:
        response = await client.get("/api/v1/admin/messages/missing")
        assert response.status_code == 404
    app.dependency_overrides.clear()
    admin_main.message_service = original_service

