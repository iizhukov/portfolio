import grpc
import pytest


class FakeRpcError(grpc.RpcError):
    def __init__(self, status_code: grpc.StatusCode, message: str):
        super().__init__()
        self._status_code = status_code
        self._message = message

    def code(self):
        return self._status_code

    def details(self):
        return self._message


pytestmark = pytest.mark.asyncio


async def test_get_projects_returns_projects(client, fake_grpc_manager):
    response = await client.get("/api/v1/projects/")
    assert response.status_code == 200
    projects = response.json()
    assert len(projects) == 1
    assert projects[0]["name"] == "Root"
    assert projects[0]["children"][0]["name"] == "Docs"
    assert fake_grpc_manager.projects_client.last_parent_id is None


async def test_get_projects_filters_by_parent(client, fake_grpc_manager):
    response = await client.get("/api/v1/projects/?parent_id=5")
    assert response.status_code == 200
    assert fake_grpc_manager.projects_client.last_parent_id == 5


async def test_get_project_detail_not_found(client, fake_grpc_manager, fake_projects_client):
    from generated.projects import projects_pb2

    fake_projects_client.project_by_id_response = projects_pb2.GetProjectByIdResponse()

    response = await client.get("/api/v1/projects/42")
    assert response.status_code == 404
    assert response.json()["detail"] == "Project not found"


async def test_get_project_detail_success(client):
    response = await client.get("/api/v1/projects/1")
    assert response.status_code == 200
    payload = response.json()
    assert payload["id"] == 1
    assert payload["name"] == "Root"


async def test_get_projects_health_success(client):
    response = await client.get("/api/v1/projects/health/")
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert payload["database"] is True


async def test_get_connections_returns_items(client):
    response = await client.get("/api/v1/connections/connections/")
    assert response.status_code == 200
    payload = response.json()
    assert len(payload) == 1
    assert payload[0]["label"] == "GitHub"
    assert payload[0]["type"] == "social"


async def test_get_connections_status_uses_cache(client, fake_redis_manager):
    response = await client.get("/api/v1/connections/status/")
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "active"


async def test_get_connections_image_success(client):
    response = await client.get("/api/v1/connections/image/")
    assert response.status_code == 200
    data = response.json()
    assert data["filename"] == "avatar.png"
    assert data["content_type"] == "image/png"


async def test_get_modules_list_services(client):
    response = await client.get("/api/v1/modules/services")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["service_name"] == "connections"


async def test_get_modules_service_details_not_found(client, fake_modules_client):
    fake_modules_client.raise_for_service["missing"] = FakeRpcError(grpc.StatusCode.NOT_FOUND, "missing")

    response = await client.get("/api/v1/modules/services/missing")
    assert response.status_code == 404
    assert response.json()["detail"] == "Service not found"


async def test_submit_admin_command_success(client, fake_admin_client):
    payload = {
        "service": "connections",
        "payload": {"action": "restart"},
    }
    response = await client.post("/api/v1/admin/commands", json=payload)

    assert response.status_code == 202
    body = response.json()
    assert body["request_id"] == "req-1"
    expected_payload = {**payload, "file": None}
    assert fake_admin_client.last_payload == expected_payload


async def test_submit_admin_command_missing_file_content(client):
    payload = {
        "service": "connections",
        "payload": {"action": "deploy"},
        "file": {"name": "report", "extension": "txt"},
    }

    response = await client.post("/api/v1/admin/commands", json=payload)
    assert response.status_code == 400
    assert response.json()["detail"] == "File content must be provided when file metadata is supplied"


async def test_get_admin_message_success(client, fake_admin_client):
    fake_admin_client.messages["req-1"] = {
        "request_id": "req-1",
        "status": "completed",
        "service": "connections",
        "payload": {"action": "restart"},
        "response": {"ok": True},
        "file": None,
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:10:00Z",
    }

    response = await client.get("/api/v1/admin/messages/req-1")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "completed"
    assert body["response"] == {"ok": True}


async def test_get_admin_message_not_found(client, fake_admin_client):
    fake_admin_client.raise_for_get = FakeRpcError(grpc.StatusCode.NOT_FOUND, "missing")

    response = await client.get("/api/v1/admin/messages/unknown")
    assert response.status_code == 404
    assert response.json()["detail"] == "Message not found"

