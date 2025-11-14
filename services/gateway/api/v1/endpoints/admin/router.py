from fastapi import APIRouter

from .endpoints import commands, messages


router = APIRouter()

router.include_router(commands.router, tags=["admin"])
router.include_router(messages.router, tags=["admin"])

__all__ = ["router"]

