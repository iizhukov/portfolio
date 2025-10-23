import logging

from typing import AsyncGenerator
from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base


logger = logging.getLogger(__name__)

Base = declarative_base()

metadata = MetaData()


class DatabaseManager:    
    def __init__(self, database_url: str):
        self.database_url = database_url
        self.engine = None
        self.async_session = None
    
    def create_engine(self):
        self.engine = create_engine(
            self.database_url,
            echo=False,
            pool_pre_ping=True,
            pool_recycle=300
        )

        logger.info("Sync engine created")
    
    def create_async_engine(self):
        self.engine = create_async_engine(
            self.database_url,
            echo=False,
            pool_pre_ping=True,
            pool_recycle=300
        )
        
        self.async_session = sessionmaker(
            self.engine,
            class_=AsyncSession,
            expire_on_commit=False
        )

        logger.info("Async engine created")

    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        if not self.async_session:
            raise RuntimeError("Async engine not initialized")
        
        async with self.async_session() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()
    
    async def close(self):
        if self.engine:
            await self.engine.dispose()
            logger.info("Database connection closed")


def create_database_url(
    user: str,
    password: str,
    host: str,
    port: str,
    database: str,
    driver: str = "postgresql+asyncpg"
) -> str:
    return f"{driver}://{user}:{password}@{host}:{port}/{database}"
