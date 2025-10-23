from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from typing import Optional

from models.image import ImageModel
from schemas.image import ImageUpdateSchema


class ImageService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_image(self) -> Optional[ImageModel]:
        result = await self.db.execute(select(ImageModel).limit(1))
        return result.scalar_one_or_none()

    async def update_image(self, image_data: ImageUpdateSchema) -> Optional[ImageModel]:
        existing_image = await self.get_image()
        
        if not existing_image:
            return None

        update_data = image_data.model_dump(exclude_unset=True)
        
        if update_data:
            await self.db.execute(
                update(ImageModel)
                .where(ImageModel.id == existing_image.id)
                .values(**update_data)
            )
            
            await self.db.flush()
        
        return existing_image
