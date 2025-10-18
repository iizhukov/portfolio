from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from datetime import datetime
import httpx

from core.config import settings
from schemas.health_check import HealthCheckResponseSchema


class HealthService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def check_health(self) -> HealthCheckResponseSchema:
        db_healthy = await self._check_database()
        redpanda_healthy = await self._check_redpanda()
        modules_healthy = await self._check_modules_service()

        overall_healthy = all([db_healthy, redpanda_healthy, modules_healthy])
        
        return HealthCheckResponseSchema(
            status="healthy" if overall_healthy else "unhealthy",
            timestamp=datetime.now(),
            database=db_healthy,
            minio=True,
            redpanda=redpanda_healthy,
            modules_service=modules_healthy
        )

    async def _check_database(self) -> bool:
        try:
            await self.db.execute(text("SELECT 1"))
            return True
        except Exception:
            return False

    async def _check_redpanda(self) -> bool:
        return True

    async def _check_modules_service(self) -> bool:
        return True
