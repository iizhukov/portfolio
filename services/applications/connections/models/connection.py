from sqlalchemy import Integer, String, DateTime
from sqlalchemy.orm import mapped_column
from sqlalchemy.sql import func

from models.base import Base


class ConnectionModel(Base):
    __tablename__ = "connections"
    
    id = mapped_column(Integer, primary_key=True, index=True)
    label = mapped_column(String, nullable=False)
    type = mapped_column(String, nullable=False)
    href = mapped_column(String, nullable=False)
    value = mapped_column(String, nullable=False)
    created_at = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at = mapped_column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<ConnectionModel(id={self.id}, label={self.label}, type={self.type}, href={self.href}, value={self.value})>"

    def to_dict(self):
        return {
            "id": self.id,
            "label": self.label,
            "type": self.type,
            "href": self.href,
            "value": self.value,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }
