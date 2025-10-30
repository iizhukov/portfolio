from sqlalchemy import Integer, String, DateTime
from sqlalchemy.orm import mapped_column

from models.base import Base


class ServicesModel(Base):
    __tablename__ = "services"

    id = mapped_column(Integer, primary_key=True, index=True)
    service_name = mapped_column(String)
    version = mapped_column(String)
    admin_topic = mapped_column(String)
    ttl_seconds = mapped_column(Integer)
    registered_at = mapped_column(DateTime)
    last_seen = mapped_column(DateTime)
    status = mapped_column(String)
    created_at = mapped_column(DateTime)
    updated_at = mapped_column(DateTime)

    def __repr__(self):
        return (
            f"<ServiceRecord(id={self.id}, service_name={self.service_name}, status={self.status})>"
        )
    
    def to_dict(self):
        return {
            "id": self.id,
            "service_name": self.service_name,
            "version": self.version,
            "admin_topic": self.admin_topic,
            "ttl_seconds": self.ttl_seconds,
            "registered_at": self.registered_at,
            "last_seen": self.last_seen,
            "status": self.status,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }
