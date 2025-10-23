from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import datetime


class StatusResponseSchema(BaseModel):
    id: int = Field(..., description="ID статуса")

    status: Literal["active", "inactive"] = Field(..., description="Статус пользователя")
    
    class Config:
        from_attributes = True


class StatusUpdateSchema(BaseModel):
    status: Literal["active", "inactive"] = Field(..., description="Статус пользователя")
