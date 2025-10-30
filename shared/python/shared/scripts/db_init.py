#!/usr/bin/env python3
from __future__ import annotations

import asyncio
import sys
from typing import Awaitable, Callable, Sequence

from sqlalchemy.ext.asyncio import create_async_engine


Initialiser = Callable[[], Awaitable[bool]]


async def _create_tables(database_url: str, base) -> bool:
    print("Initializing database...")
    print(
        "   Database URL:",
        database_url.split("@", maxsplit=1)[1] if "@" in database_url else database_url,
    )

    engine = create_async_engine(database_url, echo=False)

    try:
        async with engine.begin() as conn:
            await conn.run_sync(base.metadata.create_all)
        print("Database tables created \033[92msuccessfully\033[0m!")
        return True
    except Exception as exc:  # noqa: BLE001
        print("\033[91mError\033[0m initializing database:")
        print(f"   {exc}")
        return False
    finally:
        await engine.dispose()


async def run_database_initialization(
    *,
    service_name: str,
    database_url: str,
    base,
    tables: Sequence[str] | None = None,
    initialiser: Initialiser | None = None,
) -> bool:
    print("=" * 60)
    print(f"Database Initialization: {service_name}")
    print("=" * 60)

    if not await _create_tables(database_url, base):
        print("\n\033[91mFailed\033[0m to initialize database")
        return False

    if tables:
        print("   Tables created:")
        for tbl in tables:
            print(f"   - {tbl}")

    if initialiser is not None:
        print("\nCreating initial data...")
        try:
            success = await initialiser()
        except Exception as exc:  # noqa: BLE001
            print("\033[91mError\033[0m creating initial data:")
            print(f"   {exc}")
            success = False

        if not success:
            print("\n\033[91mFailed\033[0m to create initial data")
            return False

    print("\n" + "=" * 60)
    print("Database initialization \033[92mcompleted\033[0m!")
    print("=" * 60)
    return True


def run_initializer(**kwargs) -> None:
    if not asyncio.run(run_database_initialization(**kwargs)):
        sys.exit(1)


