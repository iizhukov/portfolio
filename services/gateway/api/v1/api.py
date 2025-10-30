from fastapi import APIRouter

from api.v1.endpoints import connections
from api.v1.endpoints.modules import router as modules_router


api_router = APIRouter()

api_router.include_router(connections.router.router, prefix="/connections")
api_router.include_router(modules_router.router, prefix="/modules")
