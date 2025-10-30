#!/usr/bin/env python3
from core.config import settings
from models.base import Base

from shared.scripts.db_init import run_initializer


def main() -> None:
    run_initializer(
        service_name="Modules",
        database_url=settings.DATABASE_URL,
        base=Base,
        tables=["services"],
        initialiser=None,
    )


if __name__ == "__main__":
    main()

