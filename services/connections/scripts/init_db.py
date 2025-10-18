import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from core.config import settings
from models.base import Base
from models import StatusModel, ConnectionModel, WorkingModel, ImageModel
from core.logging import get_logger

logger = get_logger(__name__)


async def init_database():
    engine = create_async_engine(settings.DATABASE_URL, echo=True)
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    logger.info("Database tables created successfully")

    await engine.dispose()


async def create_initial_data():
    from core.database import AsyncSessionLocal
    
    async with AsyncSessionLocal() as db:
        status = StatusModel(status="inactive")
        db.add(status)

        connections = [
            ConnectionModel(label="GitHub", type="social", href="https://github.com/iizhukov", value="iizhukov"),
            ConnectionModel(label="Email", type="email", href="mailto:iizhukov@icloud.com", value="iizhukov@icloud.com"),
            ConnectionModel(label="Telegram", type="social", href="https://t.me/ii_zhukov", value="@ii_zhukov"),
            ConnectionModel(label="VK", type="social", href="https://vk.com/ii_zhukov", value="ii_zhukov"),
        ]
        
        for conn in connections:
            db.add(conn)
        
        working = WorkingModel(working_on="Portfolio", percentage=40)
        db.add(working)

        image = ImageModel(
            filename="profile.jpg",
            content_type="image/jpeg",
            url="/storage/profile.jpg",
            size=1024000
        )
        db.add(image)

        await db.commit()
        logger.info("Initial data created successfully")


if __name__ == "__main__":
    asyncio.run(init_database())
    asyncio.run(create_initial_data())
