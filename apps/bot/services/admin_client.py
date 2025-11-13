import json
from typing import Any, Optional

import httpx

from core.config import settings


class AdminClient:
    def __init__(self, base_url: str = None):
        self.base_url = base_url or settings.ADMIN_SERVICE_URL
        self.client = httpx.AsyncClient(timeout=30.0)

    async def submit_command(
        self,
        service: str,
        command_type: str,
        data: dict[str, Any],
        file_payload: Optional[dict] = None,
    ) -> dict[str, Any]:
        payload = {
            "service": service,
            "payload": {
                "type": command_type,
                "data": data,
            },
        }

        if file_payload:
            payload["file"] = file_payload

        response = await self.client.post(
            f"{self.base_url}/api/v1/admin/commands",
            json=payload,
        )
        response.raise_for_status()
        return response.json()

    async def get_message_status(self, request_id: str) -> dict[str, Any]:
        response = await self.client.get(
            f"{self.base_url}/api/v1/admin/messages/{request_id}",
        )
        response.raise_for_status()
        return response.json()

    async def close(self):
        await self.client.aclose()

