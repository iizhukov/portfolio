from fastapi import APIRouter, HTTPException, Depends
import logging

from services.dependencies import get_grpc_manager, get_redis_manager
from services.grpc_client_manager import GrpcClientManager
from services.redis_manager import RedisManager
from services.cache_decorator import cache_response
from schemas.connections.status import StatusResponse

from generated.connections import connections_pb2

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/", response_model=StatusResponse)
@cache_response(ttl=60)
async def get_status(
    grpc_manager: GrpcClientManager = Depends(get_grpc_manager),
    redis_manager: RedisManager = Depends(get_redis_manager)
):
    try:
        connections_client = await grpc_manager.get_client("connections")
        
        request = connections_pb2.GetStatusRequest()
        response = await grpc_manager.call_grpc_with_retry(
            connections_client,
            connections_client.GetStatus,
            request,
            timeout=30
        )
        
        if not response.status:
            raise HTTPException(status_code=404, detail="Status not found")

        return StatusResponse(
            id=response.status.id,
            status=response.status.status
        )
        
    except Exception as e:
        logger.error(f"Error getting status: {e}")
        raise HTTPException(status_code=500, detail="Failed to get status")
