import logging

from fastapi import APIRouter, Depends, HTTPException

from generated.connections import connections_pb2
from schemas.connections.image import ImageResponseSchema
from services.cache_decorator import cache_response
from services.dependencies import get_grpc_manager
from services.grpc_client_manager import GrpcClientManager

from ..utils import proto_to_image


router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/", response_model=ImageResponseSchema)
@cache_response(ttl=300)
async def get_image(
    grpc_manager: GrpcClientManager = Depends(get_grpc_manager),
):
    try:
        connections_client = await grpc_manager.get_client("connections")

        response = await grpc_manager.call_grpc_with_retry(
            connections_client,
            connections_client.GetImage,
            connections_pb2.GetImageRequest(),
            timeout=30,
        )

        if not response.image:
            raise HTTPException(status_code=404, detail="Image not found")

        return proto_to_image(response.image)

    except Exception as exc:  # noqa: BLE001
        logger.error("Error getting image: %s", exc)
        raise HTTPException(status_code=500, detail="Failed to get image") from exc
