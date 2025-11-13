#!/usr/bin/env python3
import asyncio

from core.database import engine, Base
from core.logging import get_logger

from models import CommandHistory

logger = get_logger(__name__)


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables created successfully")


if __name__ == "__main__":
    asyncio.run(init_db())

