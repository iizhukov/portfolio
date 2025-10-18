from sqlalchemy import Integer, String, DateTime
from sqlalchemy.orm import mapped_column
from sqlalchemy.sql import func

from models.base import Base


class StatusModel(Base):
    __tablename__ = "status"
    
    id = mapped_column(Integer, primary_key=True, index=True)
    status = mapped_column(String, default="active")
    created_at = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at = mapped_column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<StatusModel(id={self.id}, status={self.status})>"
