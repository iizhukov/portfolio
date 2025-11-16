from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field


class AdminFileSchema(BaseModel):
    name: str
    extension: str
    path: str = ""
    content: str | None = Field(default=None, description="Base64 encoded content")
    filename: str | None = None
    content_type: str | None = None
    url: str | None = None
    bucket: str | None = None
    size: int | None = None


class AdminCommandRequestSchema(BaseModel):
    service: str
    payload: dict[str, Any]
    file: Optional[AdminFileSchema] = None


class AdminCommandResponseSchema(BaseModel):
    request_id: str
    status: str
    service: str
    payload: dict[str, Any]
    file: Optional[dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime


class AdminMessageStatusSchema(BaseModel):
    request_id: str
    status: str
    service: str
    payload: dict[str, Any]
    response: Optional[dict[str, Any]] = None
    file: Optional[dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime

