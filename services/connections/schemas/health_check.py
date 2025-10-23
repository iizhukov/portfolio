from pydantic import BaseModel, Field
from datetime import datetime
from typing import Literal


class HealthCheckResponseSchema(BaseModel):
    status: Literal["healthy", "unhealthy"] = Field(..., description="Общий статус сервиса")
    timestamp: datetime = Field(..., description="Время проверки")
    database: bool = Field(..., description="Статус базы данных")
    redpanda: bool = Field(..., description="Статус Redpanda")
    modules_service: bool = Field(..., description="Статус модулей сервиса")
