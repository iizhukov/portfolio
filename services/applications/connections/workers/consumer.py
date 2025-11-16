import os
import signal
from typing import Any, Callable, Dict, Optional

from shared.consumers import BaseAdminConsumer
from core.config import settings
from core.logging import get_logger


logger = get_logger(__name__)


class ConnectionsAdminConsumer(BaseAdminConsumer):
    def __init__(self):
        super().__init__(
            brokers=settings.MESSAGE_BROKERS,
            input_topic=settings.ADMIN_CONNECTIONS_TOPIC,
            response_topic=settings.ADMIN_RESPONSE_TOPIC,
            service_name="connections",
        )

    def get_command_handlers(self) -> Dict[str, Callable]:
        return {
            "create_connection": self._handle_create_connection,
            "update_connection": self._handle_update_connection,
            "delete_connection": self._handle_delete_connection,
            "update_status": self._handle_update_status,
            "update_working": self._handle_update_working,
            "update_image": self._handle_update_image,
            "shutdown_service": self._handle_shutdown_service,
        }

    async def _handle_create_connection(
        self, data: dict, file_info: Optional[dict] = None
    ) -> Any:
        from core.database import db_manager
        from schemas.connection import ConnectionCreateSchema
        from services.connection_service import ConnectionService
        
        async for db in db_manager.get_session():
            service = ConnectionService(db)
            connection_data = ConnectionCreateSchema(**data)
            connection = await service.create_connection(connection_data)
            logger.info(f"Created connection: {connection.id} - {connection.label}")
            return connection.to_dict()
    
    async def _handle_update_connection(
        self, data: dict, file_info: Optional[dict] = None
    ) -> Any:
        from core.database import db_manager
        from schemas.connection import ConnectionUpdateSchema
        from services.connection_service import ConnectionService
        
        connection_id = data.pop('id')
        async for db in db_manager.get_session():
            service = ConnectionService(db)
            connection_data = ConnectionUpdateSchema(**data)
            connection = await service.update_connection(connection_id, connection_data)

            if connection:
                logger.info(f"Updated connection: {connection.id} - {connection.label}")
                result = connection.to_dict()
                return result
            else:
                logger.warning(f"Connection {connection_id} not found for update")
                return None
    
    async def _handle_delete_connection(
        self, data: dict, file_info: Optional[dict] = None
    ) -> Any:
        from core.database import db_manager
        from services.connection_service import ConnectionService
        
        connection_id = data.pop('id')
        async for db in db_manager.get_session():
            service = ConnectionService(db)
            success = await service.delete_connection(connection_id)

            if success:
                logger.info(f"Deleted connection: {connection_id}")
                return {"deleted": True}
            else:
                logger.warning(f"Connection {connection_id} not found for deletion")
                return {"deleted": False}
    
    async def _handle_update_status(
        self, data: dict, file_info: Optional[dict] = None
    ) -> Any:
        from core.database import db_manager
        from services.status_service import StatusService
        
        async for db in db_manager.get_session():
            service = StatusService(db)
            status = await service.update_status(data.get('status', 'active'))
            logger.info(f"Updated status: {status.status}")
            return {"status": status.status}
    
    async def _handle_update_working(
        self, data: dict, file_info: Optional[dict] = None
    ) -> Any:
        from core.database import db_manager
        from services.working_service import WorkingService
        
        async for db in db_manager.get_session():
            service = WorkingService(db)
            working = await service.update_working_status(
                data.get('working_on', ''),
                data.get('percentage', 0)
            )
            logger.info(f"Updated working: {working.working_on} - {working.percentage}%")
            return {
                "working_on": working.working_on,
                "percentage": working.percentage
            }
    
    async def _handle_update_image(
        self, data: dict, file_info: Optional[dict] = None
    ) -> Any:
        from core.database import db_manager
        from schemas.image import ImageUpdateSchema
        from services.image_service import ImageService
        
        if file_info:
            update_data = {
                "filename": file_info.get("filename", ""),
                "content_type": file_info.get("content_type", ""),
                "url": file_info.get("url", "")
            }
        else:
            update_data = data
        
        async for db in db_manager.get_session():
            service = ImageService(db)
            image_data = ImageUpdateSchema(**update_data)
            image = await service.update_image(image_data)
            
            if image:
                logger.info(f"Updated image: {image.id} - {image.filename}")
                result = image.to_dict()
                return result
            else:
                logger.warning("Image not found for update. Image must exist first.")
                return None
    
    async def _handle_shutdown_service(
        self, data: dict, file_info: Optional[dict] = None
    ) -> Any:
        import asyncio
        
        reason = data.get('reason', 'No reason provided')
        logger.warning(f"Shutdown command received via Kafka. Reason: {reason}")

        await asyncio.sleep(0.5)
        
        logger.info("Initiating graceful shutdown...")
        os.kill(os.getpid(), signal.SIGTERM)
        return {"shutdown": True, "reason": reason}



admin_consumer = ConnectionsAdminConsumer()
