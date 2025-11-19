from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query

from core.logging import get_logger
from generated.projects import projects_pb2
from schemas.projects.projects import ProjectResponseSchema
from services.cache_decorator import cache_response
from services.dependencies import get_grpc_manager
from services.grpc_client_manager import GrpcClientManager

from ..utils import proto_project_to_schema


router = APIRouter()
logger = get_logger(__name__)


@router.get("/", response_model=List[ProjectResponseSchema])
@cache_response(ttl=300)
async def get_projects(
    parent_id: Optional[int] = Query(None, description="ID родительского проекта"),
    depth: Optional[int] = Query(None, description="Глубина загрузки детей (0 - только сам объект, 1 - прямые дети, и т.д.)"),
    grpc_manager: GrpcClientManager = Depends(get_grpc_manager),
):
    try:
        projects_client = await grpc_manager.get_client("projects")

        request = projects_pb2.GetProjectsRequest()
        if parent_id is not None:
            request.parent_id = parent_id
        if depth is not None:
            request.depth = depth

        response = await grpc_manager.call_grpc_with_retry(
            projects_client,
            projects_client.GetProjects,
            request,
            timeout=30,
        )

        projects = [proto_project_to_schema(proto) for proto in response.projects]

        logger.info("Retrieved %s projects via gRPC", len(projects))
        return projects

    except Exception as exc:  # noqa: BLE001
        logger.error("Error getting projects: %s", exc)
        raise HTTPException(status_code=500, detail="Failed to get projects") from exc


