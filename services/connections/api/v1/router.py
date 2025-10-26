from fastapi import APIRouter

from api.v1.endpoints import status, connections, working, images, health

api_router = APIRouter()

api_router.include_router(status.router, tags=["status"])
api_router.include_router(connections.router, tags=["connections"])
api_router.include_router(working.router, tags=["working"])
api_router.include_router(images.router, tags=["images"])
api_router.include_router(health.router, tags=["health"])
