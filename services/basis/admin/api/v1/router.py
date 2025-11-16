from fastapi import APIRouter

from api.v1.endpoints import admin


router = APIRouter()
router.include_router(admin.router, prefix="/admin", tags=["admin"])

__all__ = ["router"]

