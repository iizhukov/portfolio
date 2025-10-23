#!/usr/bin/env python3
import asyncio
import sys

from sqlalchemy.ext.asyncio import create_async_engine

from core.config import settings
from models.base import Base
from models import StatusModel, ConnectionModel, WorkingModel, ImageModel


async def init_database():
    print("Initializing database...")
    print(f"   Database URL: {settings.DATABASE_URL.split('@')[1] if '@' in settings.DATABASE_URL else settings.DATABASE_URL}")
    
    try:
        engine = create_async_engine(settings.DATABASE_URL, echo=False)
        
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        
        await engine.dispose()
        
        print("Database tables created \033[92msuccessfully\033[0m!")
        print("   Tables created:")
        print("   - status")
        print("   - connections")
        print("   - working")
        print("   - images")
        
        return True
        
    except Exception as e:
        print(f"\033[91mError\033[0m initializing database:")
        print(f"   {str(e)}")
        return False


async def create_initial_data():
    print("\nCreating initial data...")
    
    try:
        from core.database import db_manager
        
        async for db in db_manager.get_session():
            status = StatusModel(status="inactive")
            db.add(status)
            print("   - Status: inactive")

            connections = [
                ConnectionModel(label="GitHub", type="social", href="https://github.com/iizhukov", value="iizhukov"),
                ConnectionModel(label="Email", type="email", href="mailto:iizhukov@icloud.com", value="iizhukov@icloud.com"),
                ConnectionModel(label="Telegram", type="social", href="https://t.me/ii_zhukov", value="@ii_zhukov"),
                ConnectionModel(label="VK", type="social", href="https://vk.com/ii_zhukov", value="ii_zhukov"),
            ]
            
            for conn in connections:
                db.add(conn)
                print(f"   - Connection: {conn.label} ({conn.type})")

            working = WorkingModel(working_on="Portfolio", percentage=40)
            db.add(working)
            print("   - Working: Portfolio (40%)")

            image = ImageModel(
                filename="profile.jpg",
                content_type="image/jpeg",
                url="/storage/profile.jpg",
            )
            db.add(image)
            print("   - Image: profile.jpg")
        
        print("Initial data created \033[92msuccessfully\033[0m!")
        return True
        
    except Exception as e:
        print(f"\033[91mError\033[0m creating initial data:")
        print(f"   {str(e)}")
        return False


async def run_initialization():
    print("=" * 60)
    print("Database Initialization")
    print("=" * 60)
    
    if not await init_database():
        print("\n\033[91mFailed\033[0m to initialize database")
        sys.exit(1)
    
    if not await create_initial_data():
        print("\n\033[91mFailed\033[0m to create initial data")
        sys.exit(1)
    
    print("\n" + "=" * 60)
    print("Database initialization \033[92mcompleted\033[0m!")
    print("=" * 60)


def main():
    asyncio.run(run_initialization())


if __name__ == "__main__":
    main()
