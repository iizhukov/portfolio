from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import Optional, List

from models.file_type import FileType, VALID_FILE_TYPES


class ProjectResponseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., description="ID проекта")
    name: str = Field(..., description="Название проекта")
    type: str = Field(..., description="Тип: 'folder' или 'file'")
    file_type: Optional[str] = Field(None, description="Тип файла")
    parent_id: Optional[int] = Field(None, description="ID родительского проекта")
    url: Optional[str] = Field(None, description="URL файла в MinIO или внешняя ссылка")
    children: Optional[List["ProjectResponseSchema"]] = Field(default_factory=list, description="Вложенные проекты")
    created_at: Optional[str] = Field(None, description="Дата создания")
    updated_at: Optional[str] = Field(None, description="Дата обновления")


class ProjectCreateSchema(BaseModel):
    name: str = Field(..., description="Название проекта")
    type: str = Field(..., description="Тип: 'folder' или 'file'")
    file_type: Optional[str] = Field(None, description="Тип файла: readme, architecture, demo, github, database, swagger")
    parent_id: Optional[int] = Field(None, description="ID родительского проекта")
    url: Optional[str] = Field(None, description="URL файла в MinIO или внешняя ссылка")
    
    @field_validator('type')
    @classmethod
    def validate_type(cls, v: str) -> str:
        allowed_types = ['folder', 'file']
        if v not in allowed_types:
            raise ValueError(f"Type must be one of: {', '.join(allowed_types)}")
        return v
    
    @field_validator('file_type')
    @classmethod
    def validate_file_type(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        if v not in VALID_FILE_TYPES:
            raise ValueError(f"File type must be one of: {', '.join(VALID_FILE_TYPES)}")
        return v


class ProjectUpdateSchema(BaseModel):
    name: Optional[str] = Field(None, description="Название проекта")
    type: Optional[str] = Field(None, description="Тип: 'folder' или 'file'")
    file_type: Optional[str] = Field(None, description="Тип файла: readme, architecture, demo, github, database, swagger")
    parent_id: Optional[int] = Field(None, description="ID родительского проекта")
    url: Optional[str] = Field(None, description="URL файла в MinIO или внешняя ссылка")
    
    @field_validator('type')
    @classmethod
    def validate_type(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        allowed_types = ['folder', 'file']
        if v not in allowed_types:
            raise ValueError(f"Type must be one of: {', '.join(allowed_types)}")
        return v
    
    @field_validator('file_type')
    @classmethod
    def validate_file_type(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        if v not in VALID_FILE_TYPES:
            raise ValueError(f"File type must be one of: {', '.join(VALID_FILE_TYPES)}")
        return v

