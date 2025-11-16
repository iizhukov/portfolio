import grpc

from fastapi import APIRouter, Depends, HTTPException

from core.logging import get_logger
from schemas.admin import AdminMessageStatusSchema
from services.admin_client import AdminClient
from services.dependencies import get_admin_client


logger = get_logger(__name__)
router = APIRouter()


@router.get(
    "/messages/{request_id}",
    response_model=AdminMessageStatusSchema,
)
async def get_admin_message(
    request_id: str,
    client: AdminClient = Depends(get_admin_client),
) -> AdminMessageStatusSchema:
    try:
        response = await client.get_message(request_id)
        return AdminMessageStatusSchema.model_validate(response)
    except grpc.RpcError as exc:
        if exc.code() == grpc.StatusCode.NOT_FOUND:
            raise HTTPException(status_code=404, detail="Message not found") from exc
        logger.error("Failed to fetch admin message %s: %s", request_id, exc.details())
        raise HTTPException(status_code=502, detail=exc.details() or "Admin service error") from exc
    except Exception as exc:  # noqa: BLE001
        logger.error("Unexpected error fetching admin message %s: %s", request_id, exc)
        raise HTTPException(
            status_code=500,
            detail="Failed to fetch admin message",
        ) from exc


