from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from schemas.health_check import HealthCheckResponseSchema
from services.health_service import HealthService


router = APIRouter()


@router.get("/health-check", response_model=HealthCheckResponseSchema)
async def health_check(db: AsyncSession = Depends(get_db)):
    service = HealthService(db)
    health_status = await service.check_health()
    
    return health_status
