import asyncio
from contextlib import asynccontextmanager
from datetime import datetime, timezone

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from core.config import settings
from core.logging import get_logger
from core.database import db_manager
from sqlalchemy import text
from workers.grpc_service import serve


logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting Modules service")
    grpc_task = asyncio.create_task(serve())
    try:
        yield
    finally:
        logger.info("Shutting down Modules service")
        grpc_task.cancel()
        try:
            await grpc_task
        except asyncio.CancelledError:
            pass


app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    description="Modules registry service",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["health"], summary="Service status")
async def root() -> dict[str, str]:
    return {"service": settings.PROJECT_NAME, "status": "running"}


@app.get("/health", tags=["health"], summary="Service health")
async def health() -> dict[str, object]:
    database_ok = await _check_database()
    status = "healthy" if database_ok else "unhealthy"
    return {
        "status": status,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "database": database_ok,
    }


async def _check_database() -> bool:
    try:
        async for session in db_manager.get_session():
            await session.execute(text("SELECT 1"))
            return True
    except Exception as exc:  # noqa: BLE001
        logger.error("Database health check failed: %s", exc)
    return False


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=True,
        log_level="info",
    )
