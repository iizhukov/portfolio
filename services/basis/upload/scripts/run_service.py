#!/usr/bin/env python3
import os
import sys


def main() -> None:
    host = os.getenv("HOST", "0.0.0.0")
    port = os.getenv("PORT", "8003")

    print("=" * 60)
    print("🚀 Starting Upload Service")
    print("=" * 60)
    print(f"API: http://{host}:{port}/api/v1/upload")
    print("Press Ctrl+C to stop")
    print("=" * 60)

    os.execvp(
        "uvicorn",
        [
            "uvicorn",
            "main:app",
            "--host",
            host,
            "--port",
            port,
            "--log-level",
            "info",
        ],
    )


if __name__ == "__main__":
    main()
