from pydantic import BaseModel, Field


class HealthResponseSchema(BaseModel):
    status: str = Field(..., description="Статус сервиса")
    timestamp: str = Field(..., description="Время проверки")
    database: bool = Field(..., description="Статус базы данных")
    redpanda: bool = Field(..., description="Статус Redpanda")
    modules_service: bool = Field(..., description="Статус модулей")

