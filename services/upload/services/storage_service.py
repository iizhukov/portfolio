from __future__ import annotations

import asyncio
import io
import mimetypes
import uuid
from pathlib import PurePosixPath
from functools import partial

from minio import Minio
from minio.error import S3Error

from core.config import settings
from core.logging import get_logger


logger = get_logger(__name__)


class StorageService:
    def __init__(self, client: Minio) -> None:
        self.client = client
        self.bucket = settings.MINIO_BUCKET
        self._ensure_bucket_lock = asyncio.Lock()
        self._bucket_ready = False

    async def ensure_bucket(self) -> None:
        if self._bucket_ready:
            return
        async with self._ensure_bucket_lock:
            if self._bucket_ready:
                return
            loop = asyncio.get_running_loop()
            exists = await loop.run_in_executor(None, self.client.bucket_exists, self.bucket)
            if not exists:
                if settings.MINIO_REGION:
                    await loop.run_in_executor(
                        None, partial(self.client.make_bucket, self.bucket, location=settings.MINIO_REGION)
                    )
                else:
                    await loop.run_in_executor(None, self.client.make_bucket, self.bucket)
                logger.info("Created bucket '%s'", self.bucket)
            else:
                logger.info("Bucket '%s' already exists", self.bucket)
            self._bucket_ready = True

    async def upload_file(
        self, folder: str, filename: str, content_type: str | None, data: bytes
    ) -> tuple[str, str, str]:
        await self.ensure_bucket()

        object_name = self._build_object_name(folder, filename)
        resolved_content_type = content_type or mimetypes.guess_type(object_name)[0] or "application/octet-stream"

        loop = asyncio.get_running_loop()
        upload_task = partial(
            self.client.put_object,
            self.bucket,
            object_name,
            io.BytesIO(data),
            len(data),
            resolved_content_type,
        )
        await loop.run_in_executor(None, upload_task)

        return object_name, self._build_file_url(object_name), resolved_content_type

    def _build_object_name(self, folder: str, filename: str) -> str:
        folder_path = PurePosixPath(folder.strip("/")) if folder else PurePosixPath("")
        if filename:
            name = PurePosixPath(filename)
        else:
            name = PurePosixPath(f"{uuid.uuid4().hex}")

        object_path = folder_path / name
        return str(object_path)

    def _build_file_url(self, object_name: str) -> str:
        if settings.MINIO_EXTERNAL_URL:
            base = settings.MINIO_EXTERNAL_URL.rstrip("/")
            return f"{base}/{self.bucket}/{object_name}"
        scheme = "https" if settings.MINIO_SECURE else "http"
        return f"{scheme}://{settings.MINIO_ENDPOINT}/{self.bucket}/{object_name}"
