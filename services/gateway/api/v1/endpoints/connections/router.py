from fastapi import APIRouter

from .endpoints import connections, health, images, status, working_on


router = APIRouter()

router.include_router(connections.router, prefix="/connections", tags=["connections"])
router.include_router(status.router, prefix="/status", tags=["connections"])
router.include_router(working_on.router, prefix="/working-on", tags=["connections"])
router.include_router(images.router, prefix="/image", tags=["connections"])
router.include_router(health.router, prefix="/health", tags=["connections"])

__all__ = ["router"]
