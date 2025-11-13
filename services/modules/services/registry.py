from datetime import datetime, timedelta, timezone
from typing import Optional, Sequence

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

from core.logging import get_logger
from core.database import db_manager
from models.services import ServicesModel


logger = get_logger(__name__)


class ServiceRegistry:
    def __init__(self, default_ttl_seconds: int) -> None:
        self._default_ttl = default_ttl_seconds

    @staticmethod
    def _now() -> datetime:
        return datetime.now(timezone.utc)

    @staticmethod
    def _is_online(record: ServicesModel) -> bool:
        last_seen = record.updated_at or record.created_at or ServiceRegistry._now()
        return ServiceRegistry._now() - last_seen <= timedelta(seconds=record.ttl_seconds * 2)

    @staticmethod
    def _apply_status(record: ServicesModel) -> None:
        record.status = "ONLINE" if ServiceRegistry._is_online(record) else "OFFLINE"

    async def register(
        self,
        service_name: str,
        version: str,
        admin_topic: str,
        ttl: Optional[int] = None,
    ) -> ServicesModel:
        async for session in db_manager.get_session():
            try:
                stmt = select(ServicesModel).where(ServicesModel.service_name == service_name)
                result = await session.execute(stmt)
                record = result.scalars().first()

                now = self._now()
                ttl_seconds = ttl or self._default_ttl

                if record is None:
                    record = ServicesModel(
                        service_name=service_name,
                        version=version,
                        admin_topic=admin_topic,
                        ttl_seconds=ttl_seconds,
                        status="ONLINE",
                        created_at=now,
                        updated_at=now,
                    )
                    session.add(record)
                else:
                    record.version = version
                    record.admin_topic = admin_topic
                    record.ttl_seconds = ttl_seconds
                    record.updated_at = now
                    record.status = "ONLINE"

                await session.flush()
                await session.commit()
                return record
            except SQLAlchemyError as exc:
                logger.error("Failed to register service %s: %s", service_name, exc)
                raise

        raise RuntimeError("Failed to register service")

    async def heartbeat(self, instance_id: str) -> Optional[ServicesModel]:
        try:
            pk = int(instance_id)
        except (TypeError, ValueError):
            logger.warning("Invalid instance_id received for heartbeat: %s", instance_id)
            return None

        async for session in db_manager.get_session():
            record = await session.get(ServicesModel, pk)
            if record is None:
                return None

            record.updated_at = self._now()
            self._apply_status(record)

            await session.flush()
            await session.commit()
            return record

    async def deregister(self, instance_id: str) -> bool:
        try:
            pk = int(instance_id)
        except (TypeError, ValueError):
            logger.warning("Invalid instance_id received for deregister: %s", instance_id)
            return False

        async for session in db_manager.get_session():
            record = await session.get(ServicesModel, pk)
            if record is None:
                return False

            await session.delete(record)
            await session.flush()
            await session.commit()
            return True

        raise RuntimeError("Failed to deregister service")

    async def list_services(self) -> Sequence[ServicesModel]:
        async for session in db_manager.get_session():
            result = await session.execute(select(ServicesModel))
            records = list(result.scalars().all())
            now = self._now()

            for record in records:
                if record.updated_at is None:
                    record.updated_at = now

                previous_status = record.status
                self._apply_status(record)

                if record.status != previous_status:
                    record.updated_at = now

            await session.flush()
            await session.commit()
            return records
        
        raise RuntimeError("Failed to list services")

    async def get_admin_topic(self, service_name: str) -> Optional[ServicesModel]:
        async for session in db_manager.get_session():
            stmt = select(ServicesModel).where(ServicesModel.service_name == service_name)
            result = await session.execute(stmt)
            record = result.scalars().first()

            if record is None:
                return None

            if record.updated_at is None:
                record.updated_at = self._now()

            self._apply_status(record)
            if record.status != "ONLINE":
                return None

            await session.flush()
            await session.commit()
            return record

        raise RuntimeError("Failed to get admin topic")

    async def get_service(self, service_name: str) -> Optional[ServicesModel]:
        async for session in db_manager.get_session():
            stmt = select(ServicesModel).where(ServicesModel.service_name == service_name)
            result = await session.execute(stmt)
            record = result.scalars().first()

            if record is None:
                return None

            if record.updated_at is None:
                record.updated_at = self._now()

            self._apply_status(record)

            await session.flush()
            await session.commit()
            return record

        raise RuntimeError("Failed to get service")

