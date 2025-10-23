from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from schemas.connection import ConnectionResponseSchema
from services.connection_service import ConnectionService


router = APIRouter()


@router.get("/connections", response_model=List[ConnectionResponseSchema])
async def get_connections(db: AsyncSession = Depends(get_db)):
    service = ConnectionService(db)
    connections = await service.get_all_connections()
    return connections
