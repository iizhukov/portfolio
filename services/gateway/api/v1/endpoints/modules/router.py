from fastapi import APIRouter

from . import services


router = APIRouter()

router.include_router(services.router, prefix="/services", tags=["modules"])


__all__ = ["router"]

