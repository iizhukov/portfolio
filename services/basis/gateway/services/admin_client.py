import base64

from datetime import timezone
from typing import Any, Dict, Optional

from grpc import aio
from google.protobuf import struct_pb2
from google.protobuf.json_format import MessageToDict

from core.config import settings
from core.logging import get_logger
from generated.admin import admin_pb2, admin_pb2_grpc


logger = get_logger(__name__)


class AdminClient:
    def __init__(self) -> None:
        self._channel: Optional[aio.Channel] = None
        self._stub: Optional[admin_pb2_grpc.AdminServiceStub] = None
        self._initialized = False

    async def initialize(self) -> None:
        if self._initialized:
            return

        target = f"{settings.ADMIN_SERVICE_HOST}:{settings.ADMIN_SERVICE_PORT}"
        options = [
            ("grpc.keepalive_time_ms", 30000),
            ("grpc.keepalive_timeout_ms", 5000),
            ("grpc.keepalive_permit_without_calls", True),
        ]
        self._channel = aio.insecure_channel(target, options=options)
        self._stub = admin_pb2_grpc.AdminServiceStub(self._channel)
        self._initialized = True
        logger.info("Admin gRPC client connected to %s", target)

    async def close(self) -> None:
        if self._channel:
            await self._channel.close()
        self._channel = None
        self._stub = None
        self._initialized = False

    async def submit_command(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        await self.initialize()
        assert self._stub is not None

        payload_struct = struct_pb2.Struct()
        payload_struct.update(payload.get("payload") or {})

        request = admin_pb2.SubmitCommandRequest(
            service=payload.get("service", ""),
            payload=payload_struct,
        )

        file_data = payload.get("file")
        if isinstance(file_data, dict):
            content_str = file_data.get("content")
            content_bytes = base64.b64decode(content_str) if content_str else b""
            file_msg = admin_pb2.FilePayload(
                name=file_data.get("name", ""),
                extension=file_data.get("extension", ""),
                path=file_data.get("path", ""),
                content=content_bytes,
            )
            request.file.CopyFrom(file_msg)

        response = await self._stub.SubmitCommand(
            request,
            timeout=settings.GRPC_TIMEOUT,
        )

        return _command_response_to_dict(response)

    async def get_message(self, request_id: str) -> Dict[str, Any]:
        await self.initialize()
        assert self._stub is not None

        response = await self._stub.GetMessageStatus(
            admin_pb2.GetMessageStatusRequest(request_id=request_id),
            timeout=settings.GRPC_TIMEOUT,
        )

        return _message_status_to_dict(response)


def _struct_to_dict(message: struct_pb2.Struct | None) -> Dict[str, Any]:
    if message is None:
        return {}
    return MessageToDict(message, preserving_proto_field_name=True)


def _timestamp_to_iso(ts) -> str:
    dt = ts.ToDatetime().astimezone(timezone.utc)
    return dt.isoformat()


def _command_response_to_dict(response: admin_pb2.SubmitCommandResponse) -> Dict[str, Any]:
    result: Dict[str, Any] = {
        "request_id": response.request_id,
        "status": response.status,
        "service": response.service,
        "payload": _struct_to_dict(response.payload),
        "created_at": _timestamp_to_iso(response.created_at),
        "updated_at": _timestamp_to_iso(response.updated_at),
    }

    if response.HasField("file"):
        result["file"] = {
            "filename": response.file.filename,
            "content_type": response.file.content_type,
            "url": response.file.url,
            "bucket": response.file.bucket,
            "size": response.file.size,
        }
    else:
        result["file"] = None

    return result


def _message_status_to_dict(response: admin_pb2.MessageStatusResponse) -> Dict[str, Any]:
    result: Dict[str, Any] = {
        "request_id": response.request_id,
        "status": response.status,
        "service": response.service,
        "payload": _struct_to_dict(response.payload),
        "created_at": _timestamp_to_iso(response.created_at),
        "updated_at": _timestamp_to_iso(response.updated_at),
        "response": _struct_to_dict(response.response) if response.HasField("response") else None,
        "file": None,
    }

    if response.HasField("file"):
        result["file"] = {
            "filename": response.file.filename,
            "content_type": response.file.content_type,
            "url": response.file.url,
            "bucket": response.file.bucket,
            "size": response.file.size,
        }

    return result
