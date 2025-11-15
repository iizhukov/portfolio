#!/usr/bin/env python3
from core.config import settings
from core.database import Base
from models import CommandHistory

from shared.scripts.db_init import run_initializer


async def seed_initial_data() -> bool:
    return True


def main() -> None:
    run_initializer(
        service_name="Telegram Bot",
        database_url=settings.DATABASE_URL,
        base=Base,
        tables=["command_history"],
        initialiser=seed_initial_data,
    )


if __name__ == "__main__":
    main()

