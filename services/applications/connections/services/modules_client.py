import httpx
import asyncio
from typing import Dict, Any
from core.config import settings
from core.logging import get_logger

logger = get_logger(__name__)


class ModulesClient:
    def __init__(self):
        self.base_url = settings.MODULES_SERVICE_URL
        self.timeout = 30.0

    async def notify_connection(self, name: str, connection_type: str, action: str = "connect") -> bool:
        try:
            payload = {
                "name": name,
                "type": connection_type,
                "action": action
            }
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                if action == "connect":
                    response = await client.post(f"{self.base_url}/api/v1/connections", json=payload)
                else:  # disconnect
                    response = await client.delete(f"{self.base_url}/api/v1/connections", json=payload)
                
                if response.status_code in [200, 201, 204]:
                    logger.info(f"Successfully notified modules service about {action}: {name}")
                    return True
                else:
                    logger.error(f"Failed to notify modules service: {response.status_code} - {response.text}")
                    return False
                    
        except httpx.TimeoutException:
            logger.error(f"Timeout when notifying modules service about {action}: {name}")
            return False
        except Exception as e:
            logger.error(f"Error notifying modules service about {action}: {name} - {str(e)}")
            return False

    async def notify_emergency_disconnect(self, name: str, connection_type: str) -> bool:
        return await self.notify_connection(name, connection_type, "emergency_disconnect")

    async def health_check(self) -> bool:
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{self.base_url}/health")
                return response.status_code == 200
        except Exception:
            return False
