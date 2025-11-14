from fastapi import APIRouter

from .endpoints import list_services, service_details


router = APIRouter()

router.include_router(list_services.router, prefix="/services", tags=["modules"])
router.include_router(service_details.router, prefix="/services", tags=["modules"])


__all__ = ["router"]
