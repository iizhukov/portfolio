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
        update_data = image_data.model_dump(exclude_unset=True)
        
        if not update_data:
            return existing_image
        
        if not existing_image:
            new_image = ImageModel(
                filename=update_data.get("filename", ""),
                content_type=update_data.get("content_type", ""),
                url=update_data.get("url", "")
            )
            self.db.add(new_image)
            await self.db.commit()
            await self.db.refresh(new_image)
            return new_image
        
        await self.db.execute(
            update(ImageModel)
            .where(ImageModel.id == existing_image.id)
            .values(**update_data)
        )
        
        await self.db.commit()
        
        image = await self.get_image()
        return image
