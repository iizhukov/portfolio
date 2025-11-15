from fastapi import APIRouter, Depends

from api.v1.dependencies import require_admin_token

from .endpoints import commands, messages


router = APIRouter(dependencies=[Depends(require_admin_token)])

router.include_router(commands.router, tags=["admin"])
router.include_router(messages.router, tags=["admin"])

__all__ = ["router"]

