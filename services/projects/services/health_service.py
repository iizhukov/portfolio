from datetime import datetime
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from core.config import settings
from core.logging import get_logger

logger = get_logger(__name__)


class HealthService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def check_health(self) -> dict:
        """Проверка здоровья сервиса"""
        health_status = {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "database": False,
            "redpanda": False,
            "modules_service": False,
        }

        try:
            await self.db.execute(text("SELECT 1"))
            health_status["database"] = True
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            health_status["status"] = "unhealthy"

        if settings.MESSAGE_BROKERS:
            health_status["redpanda"] = True
        else:
            health_status["redpanda"] = False
            health_status["status"] = "unhealthy"

        if settings.MODULES_SERVICE_URL:
            health_status["modules_service"] = True
        else:
            health_status["modules_service"] = False

        return health_status

