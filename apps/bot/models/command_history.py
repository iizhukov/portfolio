from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import String, DateTime, Integer, Text, JSON
from sqlalchemy.orm import mapped_column

from core.database import Base


class CommandHistory(Base):
    __tablename__ = "command_history"

    id = mapped_column(Integer, primary_key=True, index=True)
    user_id = mapped_column(Integer, nullable=False, index=True)
    request_id = mapped_column(String, nullable=False, unique=True, index=True)
    service = mapped_column(String, nullable=False)
    command_type = mapped_column(String, nullable=False)
    payload = mapped_column(JSON, nullable=False)
    status = mapped_column(String, nullable=False, default="pending")
    response = mapped_column(JSON, nullable=True)
    error = mapped_column(Text, nullable=True)
    created_at = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "request_id": self.request_id,
            "service": self.service,
            "command_type": self.command_type,
            "payload": self.payload,
            "status": self.status,
            "response": self.response,
            "error": self.error,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

