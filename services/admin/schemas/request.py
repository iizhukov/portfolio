from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field, model_validator


class FilePayload(BaseModel):
    name: str = Field(..., description="File base name without extension")
    extension: str = Field(..., description="File extension without dot")
    path: str = Field("", description="Relative path inside the service namespace")
    content: str = Field(..., description="Base64 encoded binary content")

    @property
    def full_name(self) -> str:
        return f"{self.name}.{self.extension}".strip(".")


class AdminCommandRequest(BaseModel):
    service: str = Field(..., description="Target service name")
    payload: dict[str, Any] = Field(..., description="Service specific payload")
    file: Optional[FilePayload] = Field(
        None, description="Optional file attachment metadata and content"
    )

    @model_validator(mode="after")
    def validate_file_components(self) -> "AdminCommandRequest":
        if self.file:
            if not self.file.name or not self.file.extension:
                msg = "File must include name and extension when provided"
                raise ValueError(msg)
        return self


class AdminCommandResponse(BaseModel):
    request_id: str
    status: str
    service: str
    payload: dict[str, Any]
    file: Optional[dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime


class AdminMessageStatusResponse(BaseModel):
    request_id: str
    status: str
    service: str
    payload: dict[str, Any]
    response: Optional[dict[str, Any]]
    file: Optional[dict[str, Any]]
    created_at: datetime
    updated_at: datetime

