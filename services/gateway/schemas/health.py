from pydantic import BaseModel, Field
from typing import Dict, Any


class GatewayHealthResponse(BaseModel):
    status: str = Field(..., description="Статус gateway")
    timestamp: str = Field(..., description="Время проверки")
    redis: bool = Field(..., description="Статус Redis")
    
    model_config = {"from_attributes": True}


class ApplicationHealthResponse(BaseModel):
    status: str = Field(..., description="Общий статус приложения")
    timestamp: str = Field(..., description="Время проверки")
    services: Dict[str, Dict[str, Any]] = Field(..., description="Health 게이트way сервисов")
    infrastructure: Dict[str, bool] = Field(..., description="Health инфраструктуры")
    apps: Dict[str, bool] = Field(..., description="Health приложений")
    
    model_config = {"from_attributes": True}
