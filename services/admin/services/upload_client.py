import base64
import mimetypes
import httpx

from typing import Any, Dict

from core.config import settings
from core.logging import get_logger
from schemas.request import FilePayload


logger = get_logger(__name__)


class UploadClient:
    def __init__(self) -> None:
        self._client = httpx.AsyncClient(timeout=settings.REQUEST_TIMEOUT)

    async def close(self) -> None:
        await self._client.aclose()

    async def upload(
        self,
        service: str,
        file_payload: FilePayload,
    ) -> Dict[str, Any]:
        file_bytes = base64.b64decode(file_payload.content)

        normalized_path = file_payload.path.strip("/") if file_payload.path else ""
        if normalized_path:
            folder = f"{service}/{normalized_path}"
        else:
            folder = service

        filename = f"{file_payload.name}.{file_payload.extension}".strip(".")
        content_type = mimetypes.guess_type(filename)[0] or "application/octet-stream"

        files = {
            "folder": (None, folder),
            "filename": (None, filename),
            "file": (
                filename,
                file_bytes,
                content_type,
            ),
        }

        logger.info(
            "Uploading file for service '%s' to folder '%s' as '%s'",
            service,
            folder,
            filename,
        )

        response = await self._client.post(
            settings.UPLOAD_SERVICE_URL,
            files=files,
        )
        response.raise_for_status()

        payload = response.json()

        return {
            "filename": payload.get("object_name", filename),
            "content_type": payload.get("content_type", content_type),
            "url": payload.get("url"),
            "bucket": payload.get("bucket"),
            "size": payload.get("size"),
        }
