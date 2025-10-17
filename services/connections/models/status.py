from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func

from models.base import Base


class StatusModel(Base):
    __tablename__ = "status"
    
    id = Column(Integer, primary_key=True, index=True)
    status = Column(String, default="active")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<StatusModel(id={self.id}, status={self.status})>"
