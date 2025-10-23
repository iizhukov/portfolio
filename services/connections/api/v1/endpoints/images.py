from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from services.image_service import ImageService
from schemas.image import ImageResponseSchema, ImageUpdateSchema


router = APIRouter()


@router.get("/image", response_model=ImageResponseSchema)
async def get_image(db: AsyncSession = Depends(get_db)):
    service = ImageService(db)
    
    image = await service.get_image()

    if not image:
        raise HTTPException(status_code=404, detail="Image not found")
    
    return image
