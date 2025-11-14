import grpc
import pytest
from httpx import AsyncClient

from generated.connections import connections_pb2

pytestmark = pytest.mark.asyncio


# gRPC tests
async def test_get_connections_grpc(grpc_stub, seed_data):
    response = await grpc_stub.GetConnections(
        connections_pb2.GetConnectionsRequest()
    )

    assert len(response.connections) == 1
    connection = response.connections[0]
    assert connection.id == seed_data["connection_id"]
    assert connection.label == "GitHub"


async def test_get_image_grpc(grpc_stub, seed_data):
    response = await grpc_stub.GetImage(connections_pb2.GetImageRequest())

    assert response.image.id == seed_data["image_id"]
    assert response.image.filename == "avatar.png"
    assert response.image.content_type == "image/png"


async def test_get_image_not_found(grpc_stub, database):
    with pytest.raises(grpc.aio.AioRpcError) as exc:
        await grpc_stub.GetImage(connections_pb2.GetImageRequest())

    assert exc.value.code() == grpc.StatusCode.NOT_FOUND


async def test_get_status_grpc(grpc_stub, seed_data):
    response = await grpc_stub.GetStatus(connections_pb2.GetStatusRequest())

    assert response.status.id == seed_data["status_id"]
    assert response.status.status == "active"


async def test_get_status_not_found(grpc_stub, database):
    with pytest.raises(grpc.aio.AioRpcError) as exc:
        await grpc_stub.GetStatus(connections_pb2.GetStatusRequest())

    assert exc.value.code() == grpc.StatusCode.NOT_FOUND


async def test_get_working_grpc(grpc_stub, seed_data):
    response = await grpc_stub.GetWorking(connections_pb2.GetWorkingRequest())

    assert response.working.id == seed_data["working_id"]
    assert response.working.working_on == "Open source"
    assert response.working.percentage == 42


async def test_health_check_grpc(grpc_stub):
    response = await grpc_stub.HealthCheck(connections_pb2.HealthCheckRequest())

    assert response.status == "healthy"
    assert response.database is True
    assert response.redpanda is True
    assert response.modules_service is True


# HTTP tests
async def test_http_get_connections(http_client: AsyncClient, seed_data):
    response = await http_client.get("/api/v1/connections")

    assert response.status_code == 200
    payload = response.json()
    assert isinstance(payload, list) and len(payload) == 1
    assert payload[0]["id"] == seed_data["connection_id"]


async def test_http_get_status(http_client: AsyncClient, seed_data):
    response = await http_client.get("/api/v1/status")

    assert response.status_code == 200
    assert response.json()["status"] == "active"


async def test_http_get_status_not_found(http_client: AsyncClient, database):
    response = await http_client.get("/api/v1/status")

    assert response.status_code == 404


async def test_http_get_working(http_client: AsyncClient, seed_data):
    response = await http_client.get("/api/v1/on-working")

    assert response.status_code == 200
    data = response.json()
    assert data["working_on"] == "Open source"
    assert data["percentage"] == 42


async def test_http_get_image(http_client: AsyncClient, seed_data):
    response = await http_client.get("/api/v1/image")

    assert response.status_code == 200
    data = response.json()
    assert data["filename"] == "avatar.png"
    assert data["url"].startswith("https://cdn.example")


async def test_http_health(http_client: AsyncClient):
    response = await http_client.get("/api/v1/health")

    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
