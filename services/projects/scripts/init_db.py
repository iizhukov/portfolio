#!/usr/bin/env python3
from core.config import settings
from models.base import Base

from shared.scripts.db_init import run_initializer


async def seed_initial_data() -> bool:
    return True


def main() -> None:
    run_initializer(
        service_name="Projects",
        database_url=settings.DATABASE_URL,
        base=Base,
        tables=["projects"],
        initialiser=seed_initial_data,
    )


if __name__ == "__main__":
    main()

