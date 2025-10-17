from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class StatusBase(BaseModel):
    status: str

class StatusCreate(StatusBase):
    pass

class Status(StatusBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
