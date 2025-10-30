from fastapi import APIRouter

from api.v1.endpoints import upload


router = APIRouter()
router.include_router(upload.router, prefix="/upload", tags=["upload"])

__all__ = ["router"]
