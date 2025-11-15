import json
from pathlib import Path
from typing import Any, Optional

import httpx

from core.config import settings


class AdminClient:
    def __init__(self, base_url: str | None = None, token: str | None = None):
        self.base_url = base_url or settings.ADMIN_SERVICE_URL
        self.token = token or self._resolve_token()
        if not self.token:
            raise ValueError(
                "ADMIN_API_TOKEN must be set for authorized admin requests. "
                "Provide ADMIN_API_TOKEN or ADMIN_TOKEN_FILE env variables."
            )
        self.client = httpx.AsyncClient(
            timeout=30.0,
            headers={"Authorization": f"Bearer {self.token}"},
        )

    @staticmethod
    def _resolve_token() -> str:
        token = settings.ADMIN_API_TOKEN.strip()
        if token:
            return token
        token_path = settings.ADMIN_TOKEN_FILE.strip()
        if token_path:
            path = Path(token_path)
            if path.exists():
                return path.read_text(encoding="utf-8").strip()
        return ""

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

