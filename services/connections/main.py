import asyncio
import sys

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from core.config import settings
from core.logging import get_logger
from shared.logging.utils import disable_library_loggers
from api.v1.router import api_router
from workers.consumer import admin_consumer
from workers.grpc_service import serve as serve_grpc


disable_library_loggers()

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting Connections Service...")

    consumer_task = None

    if settings.MESSAGE_BROKERS and settings.MESSAGE_BROKERS != "":
        try:
            consumer_task = asyncio.create_task(admin_consumer.start())
            logger.info("Kafka consumer started")
        except Exception as e:
            logger.error(f"Failed to start Kafka consumer: {e}")
            sys.exit(1)
            
    else:
        logger.error("MESSAGE_BROKERS not configured")
        sys.exit(1)
    
    # grpc_task = asyncio.create_task(serve_grpc())
    
    try:
        yield
    finally:
        logger.info("Shutting down Connections Service...")

        if consumer_task:
            admin_consumer.stop()
            consumer_task.cancel()
            try:
                await consumer_task
            except asyncio.CancelledError:
                pass
        
        # grpc_task.cancel()
        # try:
        #     await grpc_task
        # except asyncio.CancelledError:
            # pass


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Connections Service",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    # allow_origins=["http://localhost:8000"],
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/")
async def root():
    return {
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "status": "running"
    }


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION
    }


if __name__ == "__main__":
    import uvicorn

    
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=True,
        log_level="info"
    )
