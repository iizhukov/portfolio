import os
import signal
import asyncio
from fastapi import APIRouter, BackgroundTasks
from pydantic import BaseModel

from core.logging import get_logger


logger = get_logger(__name__)
router = APIRouter()


class ShutdownResponse(BaseModel):
    message: str
    status: str


async def shutdown_service():
    await asyncio.sleep(1)
    logger.info("Initiating graceful shutdown...")
    os.kill(os.getpid(), signal.SIGTERM)


@router.post("/shutdown", response_model=ShutdownResponse)
async def stop_service(background_tasks: BackgroundTasks):
    logger.warning("Shutdown requested via API")
    
    background_tasks.add_task(shutdown_service)
    
    return ShutdownResponse(
        message="Service shutdown initiated",
        status="stopping"
    )

