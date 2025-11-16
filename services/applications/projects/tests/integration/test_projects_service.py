import grpc
import pytest
from httpx import AsyncClient

from generated.projects import projects_pb2


pytestmark = pytest.mark.asyncio


async def test_get_projects_returns_all(grpc_stub, seed_projects):
    response = await grpc_stub.GetProjects(projects_pb2.GetProjectsRequest())

    project_ids = sorted(project.id for project in response.projects)
    assert project_ids == sorted(seed_projects.values())


async def test_get_projects_filtered_by_parent(grpc_stub, seed_projects):
    response = await grpc_stub.GetProjects(
        projects_pb2.GetProjectsRequest(parent_id=seed_projects["root_id"])
    )

    assert len(response.projects) == 1
    project = response.projects[0]
    assert project.id == seed_projects["child_id"]
    assert project.parent_id == seed_projects["root_id"]


async def test_get_project_tree_returns_nested_structure(grpc_stub, seed_projects):
    response = await grpc_stub.GetProjectTree(projects_pb2.GetProjectTreeRequest())

    assert len(response.projects) == 1
    root = response.projects[0]
    assert root.id == seed_projects["root_id"]
    assert len(root.children) == 1
    child = root.children[0]
    assert child.id == seed_projects["child_id"]
    assert child.parent_id == seed_projects["root_id"]


async def test_get_project_by_id_not_found(grpc_stub):
    with pytest.raises(grpc.aio.AioRpcError) as exc:
        await grpc_stub.GetProjectById(projects_pb2.GetProjectByIdRequest(id=9999))

    assert exc.value.code() == grpc.StatusCode.NOT_FOUND


async def test_health_check_reports_healthy(grpc_stub):
    response = await grpc_stub.HealthCheck(projects_pb2.HealthCheckRequest())

    assert response.status == "healthy"
    assert response.database is True
    assert response.redpanda is True
    assert response.modules_service is True


async def test_http_health_endpoint(http_client: AsyncClient):
    response = await http_client.get("/api/v1/health/")

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "healthy"
    assert payload["service"] == "Projects Service"


