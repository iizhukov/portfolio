from datetime import datetime, timezone
from typing import Any, Dict, Optional

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorCollection
from pymongo import ReturnDocument

from core.config import settings
from core.logging import get_logger


logger = get_logger(__name__)


class MessageRepository:
    def __init__(self) -> None:
        self._client: Optional[AsyncIOMotorClient] = None
        self._collection: Optional[AsyncIOMotorCollection] = None

    async def connect(self) -> None:
        if self._client is not None:
            return

        self._client = AsyncIOMotorClient(settings.MONGODB_URI)
        database = self._client[settings.MONGODB_DATABASE]
        self._collection = database["messages"]
        await self._collection.create_index("request_id", unique=True)
        logger.info("Connected to MongoDB and ensured indexes")

    async def disconnect(self) -> None:
        if self._client is not None:
            self._client.close()
            self._client = None
            self._collection = None

    @property
    def collection(self) -> AsyncIOMotorCollection:
        if self._collection is None:
            raise RuntimeError("MongoDB collection not initialised")
        return self._collection

    async def create_message(
        self,
        request_id: str,
        service: str,
        payload: Dict[str, Any],
        file_info: Optional[Dict[str, Any]],
    ) -> Dict[str, Any]:
        document = {
            "request_id": request_id,
            "service": service,
            "payload": payload,
            "file": file_info,
            "status": "pending",
            "response": None,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
        }
        await self.collection.insert_one(document)
        logger.info("Stored message %s for service %s", request_id, service)
        return document

    async def mark_failed(
        self,
        request_id: str,
        error: str,
    ) -> None:
        await self.collection.update_one(
            {"request_id": request_id},
            {
                "$set": {
                    "status": "error",
                    "response": {"error": error},
                    "updated_at": datetime.now(timezone.utc),
                }
            },
        )

    async def apply_response(
        self,
        request_id: str,
        status: str,
        response: Optional[Dict[str, Any]],
    ) -> Optional[Dict[str, Any]]:
        result = await self.collection.find_one_and_update(
            {"request_id": request_id},
            {
                "$set": {
                    "status": status,
                    "response": response,
                    "updated_at": datetime.now(timezone.utc),
                }
            },
            return_document=ReturnDocument.AFTER,
        )
        if result:
            logger.info("Updated message %s with status %s", request_id, status)
        else:
            logger.warning("Message %s not found when applying response", request_id)
        return result

    async def get_message(self, request_id: str) -> Optional[Dict[str, Any]]:
        return await self.collection.find_one({"request_id": request_id})

