from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class WorkingResponseSchema(BaseModel):
    id: int = Field(..., description="ID записи")

    working_on: str = Field(..., description="Описание работы")
    percentage: int = Field(..., ge=0, le=100, description="Процент выполнения")
    
    class Config:
        from_attributes = True


class WorkingUpdateSchema(BaseModel):
    working_on: str = Field(..., description="Описание работы")
    percentage: int = Field(..., ge=0, le=100, description="Процент выполнения")
