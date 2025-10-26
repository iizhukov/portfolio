#!/usr/bin/env python3
import sys
import os


def main():
    print("=" * 60)
    print("🚀 Starting API Gateway Service")
    print("=" * 60)
    print()
    print("Server will be available at:")
    print("   - API: http://0.0.0.0:8000")
    print("   - Docs: http://0.0.0.0:8000/docs")
    print()
    print("Press Ctrl+C to stop")
    print("=" * 60)
    print()

    os.execvp("uvicorn", [
        "uvicorn",
        "main:app",
        "--host", "0.0.0.0",
        "--port", "8000",
        "--reload",
        "--log-level", "info"
    ])


if __name__ == "__main__":
    main()
