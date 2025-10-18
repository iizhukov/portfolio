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

    async def update_working_status(self, working_data: WorkingUpdateSchema) -> WorkingModel:
        existing_working = await self.get_working_status()
        
        if existing_working:
            await self.db.execute(
                update(WorkingModel)
                .where(WorkingModel.id == existing_working.id)
                .values(working_on=working_data.working_on, percentage=working_data.percentage)
            )
            await self.db.commit()
            await self.db.refresh(existing_working)

            return existing_working
        else:
            new_working = WorkingModel(
                working_on=working_data.working_on,
                percentage=working_data.percentage
            )

            self.db.add(new_working)

            await self.db.commit()
            await self.db.refresh(new_working)

            return new_working
