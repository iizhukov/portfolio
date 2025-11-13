from datetime import datetime, timezone
from typing import Optional, Sequence

from sqlalchemy import select, desc
from sqlalchemy.exc import SQLAlchemyError

from core.database import get_session
from core.logging import get_logger
from models.command_history import CommandHistory

logger = get_logger(__name__)


class HistoryService:
    async def create_command(
        self,
        user_id: int,
        request_id: str,
        service: str,
        command_type: str,
        payload: dict,
    ) -> CommandHistory:
        async for session in get_session():
            try:
                history = CommandHistory(
                    user_id=user_id,
                    request_id=request_id,
                    service=service,
                    command_type=command_type,
                    payload=payload,
                    status="pending",
                    created_at=datetime.now(timezone.utc),
                    updated_at=datetime.now(timezone.utc),
                )
                session.add(history)
                await session.commit()
                await session.refresh(history)
                return history
            except SQLAlchemyError as e:
                logger.error("Failed to create command history: %s", e)
                await session.rollback()
                raise

    async def update_command_status(
        self,
        request_id: str,
        status: str,
        response: Optional[dict] = None,
        error: Optional[str] = None,
    ) -> Optional[CommandHistory]:
        async for session in get_session():
            try:
                stmt = select(CommandHistory).where(CommandHistory.request_id == request_id)
                result = await session.execute(stmt)
                history = result.scalar_one_or_none()

                if history:
                    history.status = status
                    history.updated_at = datetime.now(timezone.utc)
                    if response is not None:
                        history.response = response
                    if error:
                        history.error = error
                    await session.commit()
                    await session.refresh(history)
                    return history
                return None
            except SQLAlchemyError as e:
                logger.error("Failed to update command history: %s", e)
                await session.rollback()
                raise

    async def get_user_history(
        self, user_id: int, limit: int = 20, offset: int = 0
    ) -> Sequence[CommandHistory]:
        async for session in get_session():
            try:
                stmt = (
                    select(CommandHistory)
                    .where(CommandHistory.user_id == user_id)
                    .order_by(desc(CommandHistory.created_at))
                    .limit(limit)
                    .offset(offset)
                )
                result = await session.execute(stmt)
                return list(result.scalars().all())
            except SQLAlchemyError as e:
                logger.error("Failed to get user history: %s", e)
                raise

    async def get_command_by_request_id(self, request_id: str) -> Optional[CommandHistory]:
        async for session in get_session():
            try:
                stmt = select(CommandHistory).where(CommandHistory.request_id == request_id)
                result = await session.execute(stmt)
                return result.scalar_one_or_none()
            except SQLAlchemyError as e:
                logger.error("Failed to get command by request_id: %s", e)
                raise

