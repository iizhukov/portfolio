from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ConnectionBase(BaseModel):
    label: str
    type: str
    href: str
    value: str


class ConnectionCreate(ConnectionBase):
    pass


class Connection(ConnectionBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
