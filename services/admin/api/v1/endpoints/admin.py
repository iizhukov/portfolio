from fastapi import APIRouter, Depends, HTTPException, status

from core.logging import get_logger
from schemas.request import (
    AdminCommandRequest,
    AdminCommandResponse,
    AdminMessageStatusResponse,
)
from services.message_service import MessageService


router = APIRouter()
logger = get_logger(__name__)


def get_message_service() -> MessageService:
    from main import message_service

    if message_service is None:
        raise RuntimeError("Message service is not initialised")
    return message_service


@router.post(
    "/commands",
    response_model=AdminCommandResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
async def submit_command(
    request: AdminCommandRequest,
    service: MessageService = Depends(get_message_service),
) -> AdminCommandResponse:
    try:
        return await service.submit_command(request)
    except RuntimeError as exc:
        logger.error("Failed to submit command: %s", exc)
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception as exc:  # noqa: BLE001
        logger.error("Unexpected error submitting command: %s", exc)
        raise HTTPException(
            status_code=500,
            detail="Failed to submit admin command",
        ) from exc


@router.get(
    "/messages/{request_id}",
    response_model=AdminMessageStatusResponse,
)
async def get_message_status(
    request_id: str,
    service: MessageService = Depends(get_message_service),
) -> AdminMessageStatusResponse:
    document = await service.get_message(request_id)
    if document is None:
        raise HTTPException(status_code=404, detail="Message not found")

    return AdminMessageStatusResponse(
        request_id=document["request_id"],
        status=document["status"],
        service=document["service"],
        payload=document.get("payload", {}),
        response=document.get("response"),
        file=document.get("file"),
        created_at=document["created_at"],
        updated_at=document["updated_at"],
    )

