import base64
import mimetypes
import grpc

from typing import Any, Dict, Optional

from grpc import aio

from core.config import settings
from core.logging import get_logger
from schemas.request import FilePayload

from generated.upload import upload_pb2, upload_pb2_grpc


logger = get_logger(__name__)


class UploadClient:
    def __init__(self) -> None:
        self._channel: Optional[aio.Channel] = None
        self._stub: Optional[upload_pb2_grpc.UploadServiceStub] = None
        self._initialized = False

    async def initialize(self) -> None:
        if self._initialized:
            return

        target = f"{settings.UPLOAD_SERVICE_GRPC_HOST}:{settings.UPLOAD_SERVICE_GRPC_PORT}"
        options = [
            ("grpc.keepalive_time_ms", 30000),
            ("grpc.keepalive_timeout_ms", 5000),
            ("grpc.keepalive_permit_without_calls", True),
        ]
        self._channel = aio.insecure_channel(target, options=options)
        self._stub = upload_pb2_grpc.UploadServiceStub(self._channel)
        self._initialized = True
        logger.info("Upload gRPC client connected to %s", target)

    async def close(self) -> None:
        if self._channel:
            await self._channel.close()
        self._channel = None
        self._stub = None
        self._initialized = False

    async def upload(
        self,
        service: str,
        file_payload: FilePayload,
    ) -> Dict[str, Any]:
        await self.initialize()
        assert self._stub is not None

        file_bytes = base64.b64decode(file_payload.content)

        normalized_path = file_payload.path.strip("/") if file_payload.path else ""
        if normalized_path:
            folder = f"{service}/{normalized_path}"
        else:
            folder = service

        filename = f"{file_payload.name}.{file_payload.extension}".strip(".")
        content_type = mimetypes.guess_type(filename)[0] or "application/octet-stream"

        logger.info(
            "Uploading file via gRPC for service '%s' to folder '%s' as '%s'",
            service,
            folder,
            filename,
        )

        request = upload_pb2.UploadRequest(
            folder=folder,
            filename=filename,
            content=file_bytes,
            content_type=content_type,
        )

        try:
            response = await self._stub.UploadFile(
                request,
                timeout=settings.REQUEST_TIMEOUT,
            )

            return {
                "filename": response.object_name,
                "content_type": response.content_type,
                "url": response.url,
                "bucket": response.bucket,
                "size": response.size,
            }
        except grpc.RpcError as e:
            logger.error("Upload failed via gRPC: %s - %s", e.code(), e.details())
            raise
