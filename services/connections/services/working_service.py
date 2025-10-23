from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from typing import Optional

from models.working import WorkingModel
from schemas.working import WorkingUpdateSchema


class WorkingService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_working_status(self) -> Optional[WorkingModel]:
        result = await self.db.execute(select(WorkingModel).limit(1))

        return result.scalar_one_or_none()

    async def update_working_status(self, working_on: str, percentage: int) -> WorkingModel:
        existing_working = await self.get_working_status()
        
        if existing_working:
            await self.db.execute(
                update(WorkingModel)
                .where(WorkingModel.id == existing_working.id)
                .values(working_on=working_on, percentage=percentage)
            )
            
            await self.db.flush()

            return existing_working
        else:
            new_working = WorkingModel(
                working_on=working_on,
                percentage=percentage
            )

            self.db.add(new_working)

            await self.db.flush()

            return new_working
