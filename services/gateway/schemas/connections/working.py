from pydantic import BaseModel, Field


class WorkingResponse(BaseModel):
    id: int = Field(..., description="ID записи")
    working_on: str = Field(..., description="Описание работы")
    percentage: int = Field(..., ge=0, le=100, description="Процент выполнения")
    
    model_config = {"from_attributes": True}
