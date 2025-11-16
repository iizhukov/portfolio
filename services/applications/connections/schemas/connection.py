from pydantic import BaseModel, Field, ConfigDict
from typing import Optional


class ConnectionResponseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., description="ID подключения")

    label: str = Field(..., description="Название подключения")
    type: str = Field(..., description="Тип подключения")
    href: str = Field(..., description="Ссылка")
    value: str = Field(..., description="Значение")


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
