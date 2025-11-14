#!/usr/bin/env python3
import uvicorn

from core.config import settings


def main():
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=False,
        log_level="info"
    )


if __name__ == "__main__":
    main()

