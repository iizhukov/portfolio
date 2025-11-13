from typing import Optional

from pydantic import BaseModel


class ModuleServiceSchema(BaseModel):
    id: int
    service_name: str
    version: str
    admin_topic: str
    ttl_seconds: int
    status: str
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


__all__ = ["ModuleServiceSchema"]

