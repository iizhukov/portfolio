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

    async def update_status(self, status: str) -> StatusModel:
        existing_status = await self.get_status()
        
        if existing_status:
            await self.db.execute(
                update(StatusModel)
                .where(StatusModel.id == existing_status.id)
                .values(status=status)
            )

            await self.db.flush()

            return existing_status
        else:
            new_status = StatusModel(status=status)

            self.db.add(new_status)

            await self.db.flush()

            return new_status
