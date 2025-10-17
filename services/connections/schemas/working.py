from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class WorkingStatusBase(BaseModel):
    label: str
    percent: int


class WorkingStatusCreate(WorkingStatusBase):
    pass


class WorkingStatus(WorkingStatusBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
