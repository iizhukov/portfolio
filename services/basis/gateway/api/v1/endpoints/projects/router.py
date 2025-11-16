from fastapi import APIRouter

from .endpoints import (
    list_projects,
    project_tree,
    project_detail,
    health,
)

router = APIRouter()

router.include_router(list_projects.router, tags=["projects"])
router.include_router(project_tree.router, tags=["projects"])
router.include_router(project_detail.router, tags=["projects"])
router.include_router(health.router, prefix="/health", tags=["projects-health"])

__all__ = ["router"]


