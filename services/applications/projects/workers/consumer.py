import os
import signal
from typing import Any, Callable, Dict, Optional

from shared.consumers import BaseAdminConsumer
from core.config import settings
from core.logging import get_logger


logger = get_logger(__name__)


class ProjectsAdminConsumer(BaseAdminConsumer):
    def __init__(self):
        super().__init__(
            brokers=settings.MESSAGE_BROKERS,
            input_topic=settings.ADMIN_PROJECTS_TOPIC,
            response_topic=settings.ADMIN_RESPONSE_TOPIC,
            service_name="projects",
        )

    def get_command_handlers(self) -> Dict[str, Callable]:
        return {
            "create_project": self._handle_create_project,
            "update_project": self._handle_update_project,
            "delete_project": self._handle_delete_project,
            "shutdown_service": self._handle_shutdown_service,
        }

    async def _handle_create_project(
        self, data: dict, file_info: Optional[dict] = None
    ) -> Any:
        from core.database import db_manager
        from schemas.project import ProjectCreateSchema
        from services.project_service import ProjectService

        data_copy = data.copy()
        
        if file_info and file_info.get('url'):
            data_copy['url'] = file_info['url']
            logger.info(f"Using uploaded file URL: {file_info['url']}")
        elif 'url' not in data_copy:
            data_copy.pop('url', None)

        async for db in db_manager.get_session():
            service = ProjectService(db)
            project_data = ProjectCreateSchema(**data_copy)
            project = await service.create_project(project_data)
            logger.info(f"Created project: {project.id} - {project.name}")
            return project.to_dict()

    async def _handle_update_project(
        self, data: dict, file_info: Optional[dict] = None
    ) -> Any:
        from core.database import db_manager
        from schemas.project import ProjectUpdateSchema
        from services.project_service import ProjectService

        data_copy = data.copy()
        project_id = data_copy.pop('id')
        
        if file_info and file_info.get('url'):
            data_copy['url'] = file_info['url']
            logger.info(f"Using uploaded file URL: {file_info['url']}")

        async for db in db_manager.get_session():
            service = ProjectService(db)
            project_data = ProjectUpdateSchema(**data_copy)
            project = await service.update_project(project_id, project_data)

            if project:
                logger.info(f"Updated project: {project.id} - {project.name}")
                result = project.to_dict()
                return result
            else:
                logger.warning(f"Project {project_id} not found for update")
                return None

    async def _handle_delete_project(
        self, data: dict, file_info: Optional[dict] = None
    ) -> Any:
        from core.database import db_manager
        from services.project_service import ProjectService

        project_id = data.pop('id')
        async for db in db_manager.get_session():
            service = ProjectService(db)
            success = await service.delete_project(project_id)

            if success:
                logger.info(f"Deleted project: {project_id}")
                return {"deleted": True}
            else:
                logger.warning(f"Project {project_id} not found for deletion")
                return {"deleted": False}

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



admin_consumer = ProjectsAdminConsumer()

