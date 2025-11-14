from pydantic import BaseModel, Field, ConfigDict
from typing import Optional


class ImageResponseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., description="ID изображения")

    filename: str = Field(..., description="Имя файла")
    content_type: str = Field(..., description="Тип контента")
    url: str = Field(..., description="URL изображения")


class ImageUpdateSchema(BaseModel):
    filename: Optional[str] = Field(None, description="Имя файла")
    content_type: Optional[str] = Field(None, description="Тип контента")
    url: Optional[str] = Field(None, description="URL изображения")
