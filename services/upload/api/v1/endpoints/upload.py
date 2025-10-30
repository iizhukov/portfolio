from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status

from schemas.upload import UploadResponse
from services.dependencies import get_storage_service
from services.storage_service import StorageService


router = APIRouter()


@router.post("", response_model=UploadResponse, status_code=status.HTTP_201_CREATED, summary="Upload file")
async def upload_file(
    folder: str = Form(..., description="Target folder within the bucket"),
    filename: Optional[str] = Form(None, description="Optional file name"),
    file: UploadFile = File(..., description="File content to upload"),
    storage: StorageService = Depends(get_storage_service),
) -> UploadResponse:
    try:
        data = await file.read()
        object_name, url, final_content_type = await storage.upload_file(
            folder=folder,
            filename=filename or file.filename or "",
            content_type=file.content_type,
            data=data,
        )
        return UploadResponse(
            url=url,
            bucket=storage.bucket,
            object_name=object_name,
            content_type=final_content_type,
            size=len(data),
        )
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=500, detail="Failed to upload file") from exc
