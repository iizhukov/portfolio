from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class ConnectionResponseSchema(BaseModel):
    id: int = Field(..., description="ID подключения")
    label: str = Field(..., description="Название подключения")
    type: str = Field(..., description="Тип подключения")
    href: str = Field(..., description="Ссылка")
    value: str = Field(..., description="Значение")
    created_at: datetime = Field(..., description="Дата создания")
    updated_at: Optional[datetime] = Field(None, description="Дата обновления")
    
    class Config:
        from_attributes = True


class ConnectionCreateSchema(BaseModel):
    label: str = Field(..., description="Название подключения")
    type: str = Field(..., description="Тип подключения")
    href: str = Field(..., description="Ссылка")
    value: str = Field(..., description="Значение")


class ConnectionUpdateSchema(BaseModel):
    label: Optional[str] = Field(None, description="Название подключения")
    type: Optional[str] = Field(None, description="Тип подключения")
    href: Optional[str] = Field(None, description="Ссылка")
    value: Optional[str] = Field(None, description="Значение")
