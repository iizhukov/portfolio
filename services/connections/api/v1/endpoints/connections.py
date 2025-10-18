from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from schemas.connection import ConnectionResponseSchema, ConnectionCreateSchema, ConnectionUpdateSchema
from services.connection_service import ConnectionService


router = APIRouter()


@router.get("/connections", response_model=List[ConnectionResponseSchema])
async def get_connections(db: AsyncSession = Depends(get_db)):
    service = ConnectionService(db)
    connections = await service.get_all_connections()
    return connections


@router.get("/connections/{connection_id}", response_model=ConnectionResponseSchema)
async def get_connection(
    connection_id: int,
    db: AsyncSession = Depends(get_db)
):
    service = ConnectionService(db)
    connection = await service.get_connection_by_id(connection_id)

    if not connection:
        raise HTTPException(status_code=404, detail="Connection not found")
    
    return connection


@router.post("/admin/connections", response_model=ConnectionResponseSchema)
async def create_connection(
    connection_data: ConnectionCreateSchema,
    db: AsyncSession = Depends(get_db)
):
    service = ConnectionService(db)
    connection = await service.create_connection(connection_data)

    return connection


@router.put("/admin/connections/{connection_id}", response_model=ConnectionResponseSchema)
async def update_connection(
    connection_id: int,
    connection_data: ConnectionUpdateSchema,
    db: AsyncSession = Depends(get_db)
):
    service = ConnectionService(db)
    connection = await service.update_connection(connection_id, connection_data)

    if not connection:
        raise HTTPException(status_code=404, detail="Connection not found")

    return connection


@router.delete("/admin/connections/{connection_id}")
async def delete_connection(
    connection_id: int,
    db: AsyncSession = Depends(get_db)
):
    service = ConnectionService(db)
    success = await service.delete_connection(connection_id)

    if not success:
        raise HTTPException(status_code=404, detail="Connection not found")

    return {"message": "Connection deleted successfully"}
