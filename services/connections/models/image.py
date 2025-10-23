from sqlalchemy import Integer, String, DateTime
from sqlalchemy.orm import mapped_column
from sqlalchemy.sql import func

from models.base import Base


class ImageModel(Base):
    __tablename__ = "images"
    
    id = mapped_column(Integer, primary_key=True, index=True)
    filename = mapped_column(String, nullable=False)
    content_type = mapped_column(String, nullable=False)
    url = mapped_column(String, nullable=False)
    created_at = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at = mapped_column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<ImageModel(id={self.id}, filename={self.filename}, url={self.url})>"

    def to_dict(self):
        return {
            "id": self.id,
            "filename": self.filename,
            "content_type": self.content_type,
            "url": self.url,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }
