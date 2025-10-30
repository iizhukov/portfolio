#!/usr/bin/env python3
from sqlalchemy import func, select

from core.config import settings
from core.database import db_manager
from models import ConnectionModel, ImageModel, StatusModel, WorkingModel
from models.base import Base

from shared.scripts.db_init import run_initializer


async def seed_initial_data() -> bool:
    async for db in db_manager.get_session():
        status_count = await db.scalar(select(func.count(StatusModel.id)))

        if status_count and status_count > 0:
            print("   Data already exists, skipping initial data creation")
            return True

        status = StatusModel(status="inactive")
        db.add(status)
        await db.flush()
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

        await db.flush()

    print("Initial data created \033[92msuccessfully\033[0m!")
    return True


def main() -> None:
    run_initializer(
        service_name="Connections",
        database_url=settings.DATABASE_URL,
        base=Base,
        tables=["status", "connections", "working", "images"],
        initialiser=seed_initial_data,
    )

if __name__ == "__main__":
    main()
