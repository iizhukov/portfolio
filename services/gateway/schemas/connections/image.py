from pydantic import BaseModel, Field


class ImageResponseSchema(BaseModel):
    id: int = Field(..., description="ID изображения")
    filename: str = Field(..., description="Имя файла")
    content_type: str = Field(..., description="Тип контента")
    url: str = Field(..., description="URL изображения")
    
    model_config = {"from_attributes": True}

