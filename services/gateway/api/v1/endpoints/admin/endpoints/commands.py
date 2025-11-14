import grpc

from fastapi import APIRouter, Depends, HTTPException, status

from core.logging import get_logger
from schemas.admin import (
    AdminCommandRequestSchema,
    AdminCommandResponseSchema,
)
from services.admin_client import AdminClient
from services.dependencies import get_admin_client


logger = get_logger(__name__)
router = APIRouter()


@router.post(
    "/commands",
    response_model=AdminCommandResponseSchema,
    status_code=status.HTTP_202_ACCEPTED,
)
async def submit_admin_command(
    request: AdminCommandRequestSchema,
    client: AdminClient = Depends(get_admin_client),
) -> AdminCommandResponseSchema:
    if request.file and request.file.content is None:
        raise HTTPException(
            status_code=400,
            detail="File content must be provided when file metadata is supplied",
        )
    try:
        response = await client.submit_command(request.model_dump())
        return AdminCommandResponseSchema.model_validate(response)
    except grpc.RpcError as exc:
        if exc.code() == grpc.StatusCode.INVALID_ARGUMENT:
            raise HTTPException(status_code=400, detail=exc.details() or "Invalid admin command") from exc
        logger.error("Admin command failed via gRPC: %s", exc.details())
        raise HTTPException(status_code=502, detail=exc.details() or "Admin service error") from exc
    except Exception as exc:  # noqa: BLE001
        logger.error("Unexpected error forwarding admin command: %s", exc)
        raise HTTPException(
            status_code=500,
            detail="Failed to submit admin command",
        ) from exc


