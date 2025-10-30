import asyncio

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from datetime import datetime

from core.config import settings
from core.logging import get_logger
from schemas.health_check import HealthCheckResponseSchema
from services.modules_client_manager import get_client as get_modules_client

logger = get_logger(__name__)


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
        try:
            from confluent_kafka.admin import AdminClient
            
            loop = asyncio.get_event_loop()
            
            def check_kafka():
                admin_client = AdminClient({'bootstrap.servers': settings.MESSAGE_BROKERS})
                metadata = admin_client.list_topics(timeout=5)
                return metadata is not None
            
            result = await loop.run_in_executor(None, check_kafka)
            return result
        except Exception as e:
            logger.error(f"Redpanda health check failed: {e}")
            return False

    async def _check_modules_service(self) -> bool:
        client = get_modules_client()
        if not client:
            logger.warning("Modules client is not configured")
            return False

        return client.is_healthy
