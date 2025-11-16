from pydantic import BaseModel, Field
from typing import Optional, List


class ProjectResponseSchema(BaseModel):
    id: int = Field(..., description="ID проекта")
    name: str = Field(..., description="Название проекта")
    type: str = Field(..., description="Тип: 'folder' или 'file'")
    file_type: Optional[str] = Field(None, description="Тип файла")
    parent_id: Optional[int] = Field(None, description="ID родительского проекта")
    url: Optional[str] = Field(None, description="URL файла в MinIO или внешняя ссылка")
    children: Optional[List["ProjectResponseSchema"]] = Field(default_factory=list, description="Вложенные проекты")
    created_at: Optional[str] = Field(None, description="Дата создания")
    updated_at: Optional[str] = Field(None, description="Дата обновления")

    model_config = {"from_attributes": True}

