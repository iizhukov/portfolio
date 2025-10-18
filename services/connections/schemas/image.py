from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class ImageResponseSchema(BaseModel):
    id: int = Field(..., description="ID изображения")
    filename: str = Field(..., description="Имя файла")
    content_type: str = Field(..., description="Тип контента")
    url: str = Field(..., description="URL изображения")
    size: Optional[int] = Field(None, description="Размер файла в байтах")
    created_at: datetime = Field(..., description="Дата создания")
    updated_at: Optional[datetime] = Field(None, description="Дата обновления")
    
    class Config:
        from_attributes = True


class ImageUpdateSchema(BaseModel):
    filename: Optional[str] = Field(None, description="Имя файла")
    content_type: Optional[str] = Field(None, description="Тип контента")
    url: Optional[str] = Field(None, description="URL изображения")
    size: Optional[int] = Field(None, description="Размер файла в байтах")
