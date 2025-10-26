from pydantic import BaseModel, Field
from typing import Literal


class StatusResponse(BaseModel):
    id: int = Field(..., description="ID статуса")
    status: Literal["active", "inactive"] = Field(..., description="Статус пользователя")
    
    model_config = {"from_attributes": True}
