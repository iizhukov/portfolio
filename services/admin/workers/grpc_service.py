import asyncio
import base64
import grpc

from datetime import datetime, timezone
from google.protobuf import struct_pb2
from google.protobuf.json_format import MessageToDict
from google.protobuf.timestamp_pb2 import Timestamp

from core.config import settings
from core.logging import get_logger
from schemas.request import AdminCommandRequest, FilePayload
from services.message_service import MessageService

from generated.admin import admin_pb2, admin_pb2_grpc


logger = get_logger(__name__)


def _dict_to_struct(data: dict | None) -> struct_pb2.Struct:
    struct = struct_pb2.Struct()
    if data:
        struct.update(data)
    return struct


def _datetime_to_timestamp(value: datetime | None) -> Timestamp:
    ts = Timestamp()
    if value is None:
        value = datetime.now(timezone.utc)
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    ts.FromDatetime(value.astimezone(timezone.utc))
    return ts


class AdminGrpcService(admin_pb2_grpc.AdminServiceServicer):
    def __init__(self, message_service: MessageService) -> None:
        self.message_service = message_service

    async def SubmitCommand(self, request: admin_pb2.SubmitCommandRequest, context: grpc.aio.ServicerContext):
        payload_dict = MessageToDict(request.payload, preserving_proto_field_name=True)

        file_payload = None
        if request.HasField("file") and request.file.name:
            content = base64.b64encode(request.file.content).decode() if request.file.content else ""
            file_payload = FilePayload(
                name=request.file.name,
                extension=request.file.extension,
                path=request.file.path,
                content=content,
            )

        command = AdminCommandRequest(
            service=request.service,
            payload=payload_dict,
            file=file_payload,
        )

        try:
            result = await self.message_service.submit_command(command)
        except RuntimeError as exc:
            context.set_code(grpc.StatusCode.UNAVAILABLE)
            context.set_details(str(exc))
            return admin_pb2.SubmitCommandResponse()
        except Exception as exc:  # noqa: BLE001
            logger.error("SubmitCommand failed: %s", exc)
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details("Failed to submit admin command")
            return admin_pb2.SubmitCommandResponse()

        response = admin_pb2.SubmitCommandResponse(
            request_id=result.request_id,
            status=result.status,
            service=result.service,
            payload=_dict_to_struct(result.payload),
            created_at=_datetime_to_timestamp(result.created_at),
            updated_at=_datetime_to_timestamp(result.updated_at),
        )

        if result.file:
            file_info = result.file
            response.file.filename = file_info.get("filename", "")
            response.file.content_type = file_info.get("content_type", "")
            response.file.url = file_info.get("url", "")
            response.file.bucket = file_info.get("bucket", "")
            size = file_info.get("size")
            if size is not None:
                response.file.size = int(size)

        return response

    async def GetMessageStatus(self, request: admin_pb2.GetMessageStatusRequest, context: grpc.aio.ServicerContext):
        document = await self.message_service.get_message(request.request_id)

        if document is None:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details("Message not found")
            return admin_pb2.MessageStatusResponse()

        response = admin_pb2.MessageStatusResponse(
            request_id=document["request_id"],
            status=document["status"],
            service=document["service"],
            payload=_dict_to_struct(document.get("payload") or {}),
            created_at=_datetime_to_timestamp(document.get("created_at")),
            updated_at=_datetime_to_timestamp(document.get("updated_at")),
        )

        response_data = document.get("response")
        if isinstance(response_data, dict) and response_data:
            response.response.CopyFrom(_dict_to_struct(response_data))

        file_info = document.get("file")
        if isinstance(file_info, dict) and file_info:
            response.file.filename = file_info.get("filename", "")
            response.file.content_type = file_info.get("content_type", "")
            response.file.url = file_info.get("url", "")
            response.file.bucket = file_info.get("bucket", "")
            size = file_info.get("size")
            if size is not None:
                response.file.size = int(size)

        return response


async def serve(message_service: MessageService) -> None:
    server = grpc.aio.server()
    admin_pb2_grpc.add_AdminServiceServicer_to_server(
        AdminGrpcService(message_service),
        server,
    )

    listen_address = f"[::]:{settings.GRPC_PORT}"
    server.add_insecure_port(listen_address)

    await server.start()
    logger.info("Admin gRPC server started on %s", listen_address)

    try:
        await server.wait_for_termination()
    except asyncio.CancelledError:
        logger.info("Stopping Admin gRPC server")
        await server.stop(5)
        raise

