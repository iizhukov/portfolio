from sqlalchemy.ext.asyncio import AsyncSession
from shared.python.database_utils import DatabaseManager
from core.config import settings


db_manager = DatabaseManager(settings.DATABASE_URL)
db_manager.create_async_engine()


async def get_db():
    async for session in db_manager.get_session():
        yield session
