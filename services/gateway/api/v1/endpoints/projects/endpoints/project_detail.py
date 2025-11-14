import grpc
from fastapi import APIRouter, Depends, HTTPException

from core.logging import get_logger
from generated.projects import projects_pb2
from schemas.projects.projects import ProjectResponseSchema
from services.cache_decorator import cache_response
from services.dependencies import get_grpc_manager
from services.grpc_client_manager import GrpcClientManager

from ..utils import proto_project_to_schema


router = APIRouter()
logger = get_logger(__name__)


@router.get("/{project_id}", response_model=ProjectResponseSchema)
@cache_response(ttl=300)
async def get_project_by_id(
    project_id: int,
    grpc_manager: GrpcClientManager = Depends(get_grpc_manager),
):
    try:
        projects_client = await grpc_manager.get_client("projects")

        request = projects_pb2.GetProjectByIdRequest(id=project_id)
        response = await grpc_manager.call_grpc_with_retry(
            projects_client,
            projects_client.GetProjectById,
            request,
            timeout=30,
        )

        if not response.HasField("project"):
            raise HTTPException(status_code=404, detail="Project not found")

        project = proto_project_to_schema(response.project)
        logger.info("Retrieved project %s via gRPC", project_id)
        return project

    except HTTPException:
        raise
    except grpc.RpcError as grpc_exc:
        if grpc_exc.code() == grpc.StatusCode.NOT_FOUND:
            logger.info("Project %s not found via gRPC", project_id)
            raise HTTPException(status_code=404, detail="Project not found")
        logger.error(
            "gRPC error getting project %s: %s - %s",
            project_id,
            grpc_exc.code(),
            grpc_exc.details(),
        )
        raise HTTPException(status_code=502, detail="Projects service unavailable") from grpc_exc
    except Exception as exc:  # noqa: BLE001
        logger.error("Error getting project %s: %s", project_id, exc)
        raise HTTPException(status_code=500, detail="Failed to get project") from exc


