import asyncio
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import Any, Optional

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.v1.router import router as api_router
from core.config import settings
from core.logging import get_logger
from services import (
    KafkaManager,
    MessageRepository,
    MessageService,
    ModulesClient,
    UploadClient,
)
from workers.grpc_service import serve as serve_grpc


logger = get_logger(__name__)

upload_client: Optional[UploadClient] = None
modules_client: Optional[ModulesClient] = None
message_repository: Optional[MessageRepository] = None
kafka_manager: Optional[KafkaManager] = None
message_service: Optional[MessageService] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global upload_client, modules_client, message_repository, kafka_manager, message_service

    logger.info("Starting Admin service")

    upload_client = UploadClient()
    modules_client = ModulesClient()
    message_repository = MessageRepository()
    kafka_manager = KafkaManager()
    message_service = MessageService(
        repository=message_repository,
        upload_client=upload_client,
        modules_client=modules_client,
        kafka_manager=kafka_manager,
    )

    await message_repository.connect()

    async def handle_response(payload: dict[str, Any]) -> None:
        if message_service is None:
            return
        await message_service.handle_response(payload)

    await kafka_manager.start_response_listener(handle_response)
    grpc_task = asyncio.create_task(serve_grpc(message_service))

    try:
        yield
    finally:
        logger.info("Shutting down Admin service")
        await kafka_manager.close()
        await upload_client.close()
        await modules_client.close()
        await message_repository.disconnect()
        grpc_task.cancel()
        try:
            await grpc_task
        except asyncio.CancelledError:
            pass
        upload_client = None
        modules_client = None
        message_repository = None
        kafka_manager = None
        message_service = None


app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    description="Admin orchestration service",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")


@app.get("/", tags=["health"], summary="Service status")
async def root() -> dict[str, str]:
    return {"service": settings.PROJECT_NAME, "status": "running"}


@app.get("/health", tags=["health"], summary="Service health")
async def health() -> dict[str, object]:
    mongo_ok = False
    try:
        if message_repository:
            await message_repository.collection.database.command("ping")
            mongo_ok = True
    except Exception as exc:  # noqa: BLE001
        logger.error("MongoDB health check failed: %s", exc)

    status = "healthy" if mongo_ok else "unhealthy"
    return {
        "status": status,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "mongodb": mongo_ok,
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=True,
        log_level=settings.LOG_LEVEL.lower(),
    )

