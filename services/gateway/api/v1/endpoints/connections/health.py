from fastapi import APIRouter, HTTPException, Depends
import logging

from services.dependencies import get_grpc_manager
from services.grpc_client_manager import GrpcClientManager
from schemas.connections.health import HealthResponse

from generated.connections import connections_pb2


router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/", response_model=HealthResponse)
async def get_connections_health(
    grpc_manager: GrpcClientManager = Depends(get_grpc_manager),
):
    try:
        connections_client = await grpc_manager.get_client("connections")
        
        response = await grpc_manager.call_grpc_with_retry(
            connections_client,
            connections_client.HealthCheck,
            connections_pb2.HealthCheckRequest(),
            timeout=10
        )
        
        return HealthResponse(
            status=response.status,
            timestamp=response.timestamp,
            database=response.database,
            redpanda=response.redpanda,
            modules_service=response.modules_service
        )

    except Exception as e:
        logger.error(f"Error getting connections health: {e}")
        raise HTTPException(status_code=500, detail="Failed to get connections health")

