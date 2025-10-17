from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional
from models import StatusModel as Model
from schemas import status as schemas


class CRUDStatus:
    async def get(self, db: AsyncSession, id: int) -> Optional[Model]:
        result = await db.execute(select(Model).filter(Model.id == id))

        return result.scalar_one_or_none()
    
    async def get_by_user(self, db: AsyncSession, user_id: str) -> Optional[Model]:
        result = await db.execute(select(Model).filter(Model.user_id == user_id))

        return result.scalar_one_or_none()
    
    async def create(self, db: AsyncSession, obj_in: schemas.StatusCreate) -> Model:
        db_obj = Model(**obj_in.dict())
        db.add(db_obj)

        await db.commit()
        await db.refresh(db_obj)

        return db_obj
    
    async def update(self, db: AsyncSession, db_obj: Model, obj_in: dict) -> Model:
        for field, value in obj_in.items():
            setattr(db_obj, field, value)

        db.add(db_obj)

        await db.commit()
        await db.refresh(db_obj)

        return db_obj
    

crud_status = CRUDStatus()
