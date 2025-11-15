from sqlalchemy import Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import mapped_column, relationship
from sqlalchemy.sql import func

from models.base import Base


class ProjectModel(Base):
    __tablename__ = "projects"
    
    id = mapped_column(Integer, primary_key=True, index=True)
    name = mapped_column(String, nullable=False)
    type = mapped_column(String, nullable=False)
    file_type = mapped_column(String, nullable=True)
    parent_id = mapped_column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=True, index=True)
    url = mapped_column(String, nullable=True, comment="URL файла в MinIO или внешняя ссылка")
    created_at = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at = mapped_column(DateTime(timezone=True), onupdate=func.now())
    
    parent = relationship("ProjectModel", remote_side=[id], back_populates="children")
    children = relationship("ProjectModel", back_populates="parent", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<ProjectModel(id={self.id}, name={self.name}, type={self.type}, parent_id={self.parent_id})>"

    def to_dict(self, include_children: bool = False):
        result = {
            "id": self.id,
            "name": self.name,
            "type": self.type,
            "file_type": self.file_type,
            "parent_id": self.parent_id,
            "url": self.url,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
        
        if include_children and self.children:
            result["children"] = [child.to_dict(include_children=True) for child in self.children]
        else:
            result["children"] = []
            
        return result

