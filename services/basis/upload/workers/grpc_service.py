import asyncio
import grpc

from core.config import settings
from core.logging import get_logger
from services.dependencies import get_storage_service
from services.storage_service import StorageService

from generated.upload import upload_pb2, upload_pb2_grpc


logger = get_logger(__name__)


class UploadGrpcService(upload_pb2_grpc.UploadServiceServicer):
    def __init__(self, storage_service: StorageService) -> None:
        self.storage_service = storage_service

    async def UploadFile(
        self,
        request: upload_pb2.UploadRequest,
        context: grpc.aio.ServicerContext,
    ) -> upload_pb2.UploadResponse:
        try:
            folder = request.folder
            filename = request.filename
            content = request.content
            content_type = request.content_type or None

            logger.info(
                "Uploading file via gRPC: folder=%s, filename=%s, size=%d bytes",
                folder,
                filename,
                len(content),
            )

            object_name, url, final_content_type = await self.storage_service.upload_file(
                folder=folder,
                filename=filename,
                content_type=content_type,
                data=content,
            )

            return upload_pb2.UploadResponse(
                url=url,
                bucket=self.storage_service.bucket,
                object_name=object_name,
                content_type=final_content_type,
                size=len(content),
            )

        except Exception as exc:  # noqa: BLE001
            logger.error("UploadFile failed: %s", exc)
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Failed to upload file: {str(exc)}")
            return upload_pb2.UploadResponse()


async def serve(storage_service: StorageService) -> None:
    server = grpc.aio.server()
    
    upload_pb2_grpc.add_UploadServiceServicer_to_server(
        UploadGrpcService(storage_service),
        server,
    )

    listen_addr = f"0.0.0.0:{settings.GRPC_PORT}"
    server.add_insecure_port(listen_addr)
    
    await server.start()
    logger.info("Upload gRPC server started on %s", listen_addr)
    
    try:
        await server.wait_for_termination()
    except KeyboardInterrupt:
        logger.info("Shutting down gRPC server...")
        await server.stop(5)

