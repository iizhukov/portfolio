import logging

from fastapi import APIRouter, Depends, HTTPException

from generated.projects import projects_pb2
from schemas.projects.health import HealthResponseSchema
from services.dependencies import get_grpc_manager
from services.grpc_client_manager import GrpcClientManager


router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/", response_model=HealthResponseSchema)
async def get_projects_health(
    grpc_manager: GrpcClientManager = Depends(get_grpc_manager),
):
    try:
        projects_client = await grpc_manager.get_client("projects")

        response = await grpc_manager.call_grpc_with_retry(
            projects_client,
            projects_client.HealthCheck,
            projects_pb2.HealthCheckRequest(),
            timeout=10,
        )

        return HealthResponseSchema(
            status=response.status,
            timestamp=response.timestamp,
            database=response.database,
            redpanda=response.redpanda,
            modules_service=response.modules_service,
        )

    except Exception as exc:  # noqa: BLE001
        logger.error("Error getting projects health: %s", exc)
        raise HTTPException(status_code=500, detail="Failed to get projects health") from exc
