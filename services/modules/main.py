import asyncio

from core.logging import get_logger
from workers.grpc_service import serve


logger = get_logger(__name__)


def main() -> None:
    logger.info("Starting Modules service")
    try:
        asyncio.run(serve())
    except KeyboardInterrupt:
        logger.info("Stopping Modules service")


if __name__ == "__main__":
    main()
