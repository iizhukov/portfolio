from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import datetime


class StatusResponseSchema(BaseModel):
    id: int = Field(..., description="ID статуса")
    status: Literal["active", "inactive"] = Field(..., description="Статус пользователя")
    created_at: datetime = Field(..., description="Дата создания")
    updated_at: Optional[datetime] = Field(None, description="Дата обновления")
    
    class Config:
        from_attributes = True


class StatusUpdateSchema(BaseModel):
    status: Literal["active", "inactive"] = Field(..., description="Статус пользователя")
