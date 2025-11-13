from pydantic import BaseModel, Field
from typing import Literal


class HealthResponseSchema(BaseModel):
    status: Literal["healthy", "unhealthy"] = Field(..., description="Общий статус сервиса")
    timestamp: str = Field(..., description="Время проверки")
    database: bool = Field(..., description="Статус базы данных")
    redpanda: bool = Field(..., description="Статус Redpanda")
    modules_service: bool = Field(..., description="Статус модулей сервиса")
    
    model_config = {"from_attributes": True}

