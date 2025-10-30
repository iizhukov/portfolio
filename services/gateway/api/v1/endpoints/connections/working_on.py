import logging

from fastapi import APIRouter, HTTPException, Depends

from services.dependencies import get_grpc_manager
from services.grpc_client_manager import GrpcClientManager
from services.cache_decorator import cache_response
from schemas.connections.working import WorkingResponse

from generated.connections import connections_pb2


router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/", response_model=WorkingResponse)
@cache_response(ttl=60)
async def get_working_on(
    grpc_manager: GrpcClientManager = Depends(get_grpc_manager),
):
    try:
        connections_client = await grpc_manager.get_client("connections")
        
        request = connections_pb2.GetWorkingRequest()
        response = await grpc_manager.call_grpc_with_retry(
            connections_client,
            connections_client.GetWorking,
            request,
            timeout=30
        )
        
        if not response.working:
            raise HTTPException(status_code=404, detail="Working status not found")
        
        return WorkingResponse(
            id=response.working.id,
            working_on=response.working.working_on,
            percentage=response.working.percentage
        )
        
    except Exception as e:
        logger.error(f"Error getting working status: {e}")
        raise HTTPException(status_code=500, detail="Failed to get working status")
