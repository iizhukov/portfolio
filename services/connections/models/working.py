from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func

from connections.models.base import Base


class WorkingModel(Base):
    __tablename__ = "working"
    
    id = Column(Integer, primary_key=True, index=True)
    working_on = Column(String, default=True)
    percentage = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<WorkingModel(id={self.id}, working_on={self.working_on}, percentage={self.percentage})>"

    def to_dict(self):
        return {
            "id": self.id,
            "working_on": self.working_on,
            "percentage": self.percentage,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }
