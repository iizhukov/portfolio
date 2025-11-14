#!/usr/bin/env python3
import asyncio

from core.database import db_manager
from core.logging import get_logger
from models.project import ProjectModel
from models.base import Base

logger = get_logger(__name__)


async def main():
    async with db_manager.engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables created successfully")


if __name__ == "__main__":
    asyncio.run(main())

