from typing import List

from fastapi import APIRouter, Depends, HTTPException

from core.logging import get_logger
from generated.connections import connections_pb2
from schemas.connections.connections import ConnectionResponseSchema
from services.cache_decorator import cache_response
from services.dependencies import get_grpc_manager
from services.grpc_client_manager import GrpcClientManager

from ..utils import proto_to_connection


router = APIRouter()
logger = get_logger(__name__)


@router.get("/", response_model=List[ConnectionResponseSchema])
@cache_response(ttl=300)
async def get_connections(
    grpc_manager: GrpcClientManager = Depends(get_grpc_manager),
):
    try:
        connections_client = await grpc_manager.get_client("connections")

        response = await grpc_manager.call_grpc_with_retry(
            connections_client,
            connections_client.GetConnections,
            connections_pb2.GetConnectionsRequest(),
            timeout=30,
        )

        connections = [proto_to_connection(conn) for conn in response.connections]
        logger.info("Retrieved %s connections via gRPC", len(connections))
        return connections

    except Exception as exc:  # noqa: BLE001
        logger.error("Error getting connections: %s", exc)
        raise HTTPException(status_code=500, detail="Failed to get connections") from exc
