from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from typing import Optional, Sequence

from models.connection import ConnectionModel
from schemas.connection import ConnectionCreateSchema, ConnectionUpdateSchema


class ConnectionService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all_connections(self) -> Sequence[ConnectionModel]:
        result = await self.db.execute(select(ConnectionModel))

        return result.scalars().all()

    async def get_connection_by_id(self, connection_id: int) -> Optional[ConnectionModel]:
        result = await self.db.execute(select(ConnectionModel).where(ConnectionModel.id == connection_id))

        return result.scalar_one_or_none()

    async def create_connection(self, connection_data: ConnectionCreateSchema) -> ConnectionModel:
        new_connection = ConnectionModel(
            label=connection_data.label,
            type=connection_data.type,
            href=connection_data.href,
            value=connection_data.value
        )

        self.db.add(new_connection)

        await self.db.flush()

        return new_connection

    async def update_connection(self, connection_id: int, connection_data: ConnectionUpdateSchema) -> Optional[ConnectionModel]:
        connection = await self.get_connection_by_id(connection_id)
        
        if not connection:
            return None

        update_data = connection_data.model_dump(exclude_unset=True)
        if update_data:
            await self.db.execute(
                update(ConnectionModel)
                .where(ConnectionModel.id == connection_id)
                .values(**update_data)
            )

            await self.db.flush()
        
        return connection

    async def delete_connection(self, connection_id: int) -> bool:
        result = await self.db.execute(delete(ConnectionModel).where(ConnectionModel.id == connection_id))

        await self.db.flush()

        return result.all().count(1) > 0
