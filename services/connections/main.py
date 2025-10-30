import asyncio
import sys

from typing import Optional
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from core.config import settings
from core.logging import get_logger
from api.v1.router import api_router
from workers.consumer import admin_consumer
from workers.grpc_service import serve as serve_grpc
from services.modules_client_manager import set_client as set_modules_client

from shared.clients import ModulesClient, RegistrationParams
from shared.logging.utils import disable_library_loggers

disable_library_loggers()

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting Connections Service...")

    consumer_task = None
    modules_client: Optional[ModulesClient] = None

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
    
    modules_client = ModulesClient(
        target=settings.MODULES_SERVICE_URL,
        registration=RegistrationParams(
            service_name="connections",
            version=settings.VERSION,
            admin_topic=settings.ADMIN_CONNECTIONS_TOPIC,
        ),
        heartbeat_interval=
            settings.MODULES_HEARTBEAT_INTERVAL if settings.MODULES_HEARTBEAT_INTERVAL > 0 else None,
    )

    try:
        await modules_client.start()
        logger.info("Registered with modules service")
        set_modules_client(modules_client)
        app.state.modules_client = modules_client
    except Exception as exc:  # noqa: BLE001
        logger.error("Failed to register with modules service: %s", exc)
        sys.exit(1)

    grpc_task = asyncio.create_task(serve_grpc())
    logger.info("gRPC server started")
    
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
        
        if modules_client:
            try:
                await modules_client.stop()
            except Exception as exc:  # noqa: BLE001
                logger.warning("Failed to deregister from modules service: %s", exc)
            finally:
                set_modules_client(None)
                app.state.modules_client = None

        if grpc_task:
            grpc_task.cancel()
            try:
                await grpc_task
            except asyncio.CancelledError:
                pass


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
