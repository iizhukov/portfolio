from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class WorkingResponseSchema(BaseModel):
    id: int = Field(..., description="ID записи")
    working_on: str = Field(..., description="Описание работы")
    percentage: int = Field(..., ge=0, le=100, description="Процент выполнения")
    created_at: datetime = Field(..., description="Дата создания")
    updated_at: Optional[datetime] = Field(None, description="Дата обновления")
    
    class Config:
        from_attributes = True


class WorkingUpdateSchema(BaseModel):
    working_on: str = Field(..., description="Описание работы")
    percentage: int = Field(..., ge=0, le=100, description="Процент выполнения")
