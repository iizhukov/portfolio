from pydantic import BaseModel, Field, ConfigDict
from typing import Literal


class StatusResponseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., description="ID статуса")

    status: Literal["active", "inactive"] = Field(..., description="Статус пользователя")


class StatusUpdateSchema(BaseModel):
    status: Literal["active", "inactive"] = Field(..., description="Статус пользователя")
