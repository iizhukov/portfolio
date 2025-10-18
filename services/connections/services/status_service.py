from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from typing import Optional

from models.status import StatusModel
from schemas.status import StatusUpdateSchema


class StatusService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_status(self) -> Optional[StatusModel]:
        result = await self.db.execute(select(StatusModel).limit(1))
        return result.scalar_one_or_none()

    async def update_status(self, status_data: StatusUpdateSchema) -> StatusModel:
        existing_status = await self.get_status()
        
        if existing_status:
            await self.db.execute(
                update(StatusModel)
                .where(StatusModel.id == existing_status.id)
                .values(status=status_data.status)
            )
            await self.db.commit()
            await self.db.refresh(existing_status)
            return existing_status
        else:
            new_status = StatusModel(status=status_data.status)
            self.db.add(new_status)
            await self.db.commit()
            await self.db.refresh(new_status)
            return new_status
