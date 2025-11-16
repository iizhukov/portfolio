from datetime import datetime, timezone
from typing import Any, Dict, Optional
from uuid import uuid4

from core.logging import get_logger
from schemas.request import AdminCommandRequest, AdminCommandResponse
from .kafka_manager import KafkaManager
from .message_repository import MessageRepository
from .modules_client import ModulesClient
from .upload_client import UploadClient


logger = get_logger(__name__)


class MessageService:
    def __init__(
        self,
        repository: MessageRepository,
        upload_client: UploadClient,
        modules_client: ModulesClient,
        kafka_manager: KafkaManager,
    ) -> None:
        self._repository = repository
        self._upload_client = upload_client
        self._modules_client = modules_client
        self._kafka_manager = kafka_manager

    async def submit_command(
        self,
        command: AdminCommandRequest,
    ) -> AdminCommandResponse:
        request_id = str(uuid4())
        upload_info: Optional[Dict[str, Any]] = None

        if command.file:
            upload_info = await self._upload_client.upload(
                command.service,
                command.file,
            )

        record = await self._repository.create_message(
            request_id=request_id,
            service=command.service,
            payload=command.payload,
            file_info=upload_info,
        )

        topic = await self._modules_client.get_admin_topic(command.service)
        if not topic:
            await self._repository.mark_failed(
                request_id,
                f"Service '{command.service}' is not registered or offline",
            )
            raise RuntimeError("Target service is unavailable")

        message_payload = {
            "request_id": request_id,
            "service": command.service,
            "payload": command.payload,
            "file": upload_info,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        await self._kafka_manager.send(topic, message_payload)

        return AdminCommandResponse(
            request_id=request_id,
            status=record["status"],
            service=record["service"],
            payload=record["payload"],
            file=record.get("file"),
            created_at=record["created_at"],
            updated_at=record["updated_at"],
        )

    async def handle_response(self, message: dict[str, Any]) -> None:
        request_id = message.get("request_id")
        service = message.get("service")
        status = message.get("status", "completed")
        response = message.get("response")
        error = message.get("error")

        combined_response: Optional[Dict[str, Any]] = None
        if isinstance(response, dict):
            combined_response = dict(response)
        elif response is not None:
            combined_response = {"data": response}

        if error:
            if combined_response is None:
                combined_response = {}
            combined_response["error"] = error

        if not request_id:
            logger.warning("Received admin response without request_id: %s", message)
            return

        logger.info(
            "Received response for request %s from service %s with status %s",
            request_id,
            service,
            status,
        )

        await self._repository.apply_response(
            request_id=request_id,
            status=status,
            response=combined_response,
        )

    async def get_message(self, request_id: str) -> Optional[Dict[str, Any]]:
        return await self._repository.get_message(request_id)

