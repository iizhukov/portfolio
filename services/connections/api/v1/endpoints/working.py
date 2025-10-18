from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from schemas.working import WorkingResponseSchema, WorkingUpdateSchema
from services.working_service import WorkingService


router = APIRouter()


@router.get("/on-working", response_model=WorkingResponseSchema)
async def get_working_status(db: AsyncSession = Depends(get_db)):
    service = WorkingService(db)
    working = await service.get_working_status()

    if not working:
        raise HTTPException(status_code=404, detail="Working status not found")

    return working


@router.put("/admin/on-working", response_model=WorkingResponseSchema)
async def update_working_status(
    working_data: WorkingUpdateSchema,
    db: AsyncSession = Depends(get_db)
):
    service = WorkingService(db)
    working = await service.update_working_status(working_data)

    return working
