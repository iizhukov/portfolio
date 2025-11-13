import asyncio

from contextlib import asynccontextmanager
from datetime import datetime, timezone

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.v1.router import router as api_router
from core.config import settings
from core.logging import get_logger
from services.dependencies import get_storage_service
from minio.error import S3Error


logger = get_logger(__name__)



@asynccontextmanager
async def lifespan(app: FastAPI):
    storage = get_storage_service()
    await storage.ensure_bucket()
    
    from workers.grpc_service import serve as serve_grpc
    grpc_task = asyncio.create_task(serve_grpc(storage))
    
    logger.info("Upload service started (HTTP and gRPC)")

    try:
        yield
    finally:
        logger.info("Shutting down Upload service...")
        grpc_task.cancel()
        try:
            await grpc_task
        except asyncio.CancelledError:
            pass
        logger.info("Upload service stopped")


app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    description="File upload service",
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
    return {
        "service": settings.PROJECT_NAME,
        "status": "running",
    }


@app.get("/health", tags=["health"], summary="Service health")
async def health() -> dict[str, object]:
    minio_ok = await _check_minio()
    status = "healthy" if minio_ok else "unhealthy"
    return {
        "status": status,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "minio": minio_ok,
    }


async def _check_minio() -> bool:
    storage = get_storage_service()
    loop = asyncio.get_running_loop()
    try:
        await loop.run_in_executor(None, storage.client.list_buckets)
        return True
    except S3Error as exc:  # noqa: BLE001
        logger.error("MinIO health check failed: %s", exc)
    except Exception as exc:  # noqa: BLE001
        logger.error("Unexpected error during MinIO health check: %s", exc)
    return False


if __name__ == "__main__":
    import uvicorn

    
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=True,
        log_level="info"
    )
