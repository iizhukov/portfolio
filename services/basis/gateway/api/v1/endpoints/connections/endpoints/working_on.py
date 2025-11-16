import logging

from fastapi import APIRouter, Depends, HTTPException

from generated.connections import connections_pb2
from schemas.connections.working import WorkingResponseSchema
from services.cache_decorator import cache_response
from services.dependencies import get_grpc_manager
from services.grpc_client_manager import GrpcClientManager

from ..utils import proto_to_working


router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/", response_model=WorkingResponseSchema)
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
            timeout=30,
        )

        if not response.working:
            raise HTTPException(status_code=404, detail="Working status not found")

        return proto_to_working(response.working)

    except Exception as exc:  # noqa: BLE001
        logger.error("Error getting working status: %s", exc)
        raise HTTPException(status_code=500, detail="Failed to get working status") from exc
