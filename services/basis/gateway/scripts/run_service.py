#!/usr/bin/env python3
import sys
import os

from scripts.admin_token import ensure_admin_token


def main():
    token = ensure_admin_token()
    print("=" * 60)
    print("🚀 Starting API Gateway Service")
    print("=" * 60)
    print()
    print("Server will be available at:")
    print("   - API: http://0.0.0.0:8000")
    print("   - Docs: http://0.0.0.0:8000/docs")
    print()
    print("Admin API token (add to Authorization header as 'Bearer <token>'):")
    print(f"   {token}")
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
