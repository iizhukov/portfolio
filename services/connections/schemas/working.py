from pydantic import BaseModel, Field, ConfigDict


class WorkingResponseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., description="ID записи")

    working_on: str = Field(..., description="Описание работы")
    percentage: int = Field(..., ge=0, le=100, description="Процент выполнения")


class WorkingUpdateSchema(BaseModel):
    working_on: str = Field(..., description="Описание работы")
    percentage: int = Field(..., ge=0, le=100, description="Процент выполнения")
