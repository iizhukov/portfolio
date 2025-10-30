from pydantic import BaseModel


class UploadResponse(BaseModel):
    url: str
    bucket: str
    object_name: str
    content_type: str
    size: int


__all__ = ["UploadResponse"]
