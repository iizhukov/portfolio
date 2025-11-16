from sqlalchemy import Integer, String, DateTime
from sqlalchemy.orm import mapped_column
from sqlalchemy.sql import func

from models.base import Base


class WorkingModel(Base):
    __tablename__ = "working"
    
    id = mapped_column(Integer, primary_key=True, index=True)
    working_on = mapped_column(String, default="")
    percentage = mapped_column(Integer, default=0)
    created_at = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at = mapped_column(DateTime(timezone=True), onupdate=func.now())

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
