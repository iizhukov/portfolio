import logging

from fastapi import APIRouter, HTTPException, Depends

from services.dependencies import get_grpc_manager
from services.grpc_client_manager import GrpcClientManager
from services.cache_decorator import cache_response
from schemas.connections.image import ImageResponse

from generated import connections_pb2


router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/", response_model=ImageResponse)
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
            timeout=30
        )
        
        if not response.image:
            raise HTTPException(status_code=404, detail="Image not found")
        
        return ImageResponse(
            id=response.image.id,
            filename=response.image.filename,
            content_type=response.image.content_type,
            url=response.image.url
        )
        
    except Exception as e:
        logger.error(f"Error getting image: {e}")
        raise HTTPException(status_code=500, detail="Failed to get image")

