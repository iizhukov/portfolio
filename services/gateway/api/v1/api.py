from fastapi import APIRouter

from api.v1.endpoints.connections import router as connections_router
from api.v1.endpoints.admin import router as admin_router
from api.v1.endpoints.modules import router as modules_router


api_router = APIRouter()

api_router.include_router(connections_router, prefix="/connections")
api_router.include_router(modules_router, prefix="/modules")
api_router.include_router(admin_router, prefix="/admin")
