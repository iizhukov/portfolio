from fastapi import APIRouter, HTTPException, Depends
from typing import List

from services.dependencies import get_grpc_manager
from services.grpc_client_manager import GrpcClientManager
from services.cache_decorator import cache_response
from schemas.connections.connections import ConnectionResponseSchema
from core.logging import get_logger

from generated.connections import connections_pb2


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
            timeout=30
        )
        
        connections = []
        for conn in response.connections:
            connections.append(ConnectionResponseSchema(
                id=conn.id,
                label=conn.label,
                type=conn.type,
                href=conn.href,
                value=conn.value,
            ))
        
        logger.info(f"Retrieved {len(connections)} connections via gRPC")
        return connections
        
    except Exception as e:
        logger.error(f"Error getting connections: {e}")
        raise HTTPException(status_code=500, detail="Failed to get connections")
