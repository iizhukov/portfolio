from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from core.config import settings
from core.logging import get_logger
from shared.logging.utils import disable_library_loggers
from api.v1.api import api_router
from services.dependencies import initialize_services, close_services


disable_library_loggers()

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting API Gateway...")
    
    await initialize_services()
    
    try:
        yield
    finally:
        logger.info("Shutting down API Gateway...")
        await close_services()


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="API Gateway",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173", "http://localhost:8080"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/")
async def root():
    from services.dependencies import get_grpc_manager
    grpc_manager = get_grpc_manager()
    
    return {
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "status": "running",
        "grpc_services": await grpc_manager.get_available_services()
    }


@app.get("/health")
async def health_check():
    from services.dependencies import get_redis_manager
    from datetime import datetime
    
    redis_manager = get_redis_manager()
    redis_healthy = await redis_manager.health_check()
    
    all_healthy = redis_healthy
    
    return {
        "status": "healthy" if all_healthy else "unhealthy",
        "timestamp": datetime.now().isoformat(),
        "redis": redis_healthy
    }


@app.get("/health/app")
async def application_health_check():
    from services.dependencies import get_grpc_manager, get_redis_manager
    import httpx
    from datetime import datetime
    
    grpc_manager = get_grpc_manager()
    redis_manager = get_redis_manager()
    
    services_health = {}
    infrastructure_health = {}
    apps_health = {}
    
    connections_health = None
    try:
        connections_client = await grpc_manager.get_client("connections")
        from generated.connections import connections_pb2
        health_response = await grpc_manager.call_grpc_with_retry(
            connections_client,
            connections_client.HealthCheck,
            connections_pb2.HealthCheckRequest(),
            timeout=5.0
        )
        
        connections_health = {
            "status": health_response.status,
            "timestamp": health_response.timestamp,
            "database": health_response.database,
            "redpanda": health_response.redpanda,
            "modules_service": health_response.modules_service
        }
    except Exception as e:
        logger.error(f"Failed to get connections health via gRPC: {e}")
    
    if connections_health:
        services_health["connections"] = connections_health
    
    if connections_health:
        infrastructure_health["postgresql"] = connections_health.get("database", False)
        infrastructure_health["redpanda"] = connections_health.get("redpanda", False)
    
    redis_healthy = await redis_manager.health_check()
    infrastructure_health["redis"] = redis_healthy
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get("http://nginx/health/nginx", timeout=2.0)
            infrastructure_health["nginx"] = response.status_code == 200
    except Exception:
        infrastructure_health["nginx"] = False
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get("http://minio:9000/minio/health/live", timeout=2.0)
            infrastructure_health["minio"] = response.status_code == 200
    except Exception:
        infrastructure_health["minio"] = False
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get("http://web-client/", timeout=2.0)
            apps_health["web"] = response.status_code < 500
    except Exception:
        apps_health["web"] = False
    
    all_services_healthy = all(
        service.get("status") == "healthy" for service in services_health.values()
    ) if services_health else False
    all_infrastructure_healthy = all(infrastructure_health.values())
    all_apps_healthy = all(apps_health.values())
    
    overall_status = "healthy" if (all_services_healthy and all_infrastructure_healthy and all_apps_healthy) else "unhealthy"
    
    return {
        "status": overall_status,
        "timestamp": datetime.now().isoformat(),
        "services": services_health,
        "infrastructure": infrastructure_health,
        "apps": apps_health
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
