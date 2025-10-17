from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func

from models.base import Base


class ConnectionModel(Base):
    __tablename__ = "connections"
    
    id = Column(Integer, primary_key=True, index=True)
    label = Column(String, nullable=False)
    type = Column(String, nullable=False)
    href = Column(String, nullable=False)
    value = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

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
