from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from schemas.status import StatusResponseSchema, StatusUpdateSchema
from services.status_service import StatusService


router = APIRouter()


@router.get("/status", response_model=StatusResponseSchema)
async def get_status(db: AsyncSession = Depends(get_db)):
    service = StatusService(db)
    status = await service.get_status()

    if not status:
        raise HTTPException(status_code=404, detail="Status not found")

    return status
