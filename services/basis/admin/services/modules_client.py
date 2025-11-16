import asyncio
import grpc

from typing import Optional

from core.config import settings
from core.logging import get_logger

from generated.modules import modules_pb2, modules_pb2_grpc


logger = get_logger(__name__)


class ModulesClient:
    def __init__(self) -> None:
        target = f"{settings.MODULES_GRPC_HOST}:{settings.MODULES_GRPC_PORT}"
        self._channel = grpc.aio.insecure_channel(target)
        self._stub = modules_pb2_grpc.ModulesServiceStub(self._channel)
        self._lock = asyncio.Lock()

    async def close(self) -> None:
        await self._channel.close()

    async def get_admin_topic(self, service_name: str) -> Optional[str]:
        async with self._lock:
            request = modules_pb2.GetServiceRequest(service_name=service_name)
            response = await self._stub.GetService(request)

        if not response.service.service_name:
            logger.warning("Service '%s' not found in modules registry", service_name)
            return None

        topic = response.service.admin_topic
        logger.info(
            "Fetched admin topic '%s' for service '%s'", topic, service_name
        )
        return topic

