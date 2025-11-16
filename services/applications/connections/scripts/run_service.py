#!/usr/bin/env python3
import sys
import os


def main():
    print("=" * 60)
    print("🚀 Starting Connections Service")
    print("=" * 60)
    print()
    print("Server will be available at:")
    print("   - API: http://0.0.0.0:8002")
    print("   - Docs: http://0.0.0.0:8002/docs")
    print("   - gRPC: 0.0.0.0:50051")
    print()
    print("Press Ctrl+C to stop")
    print("=" * 60)
    print()
    
    os.execvp("uvicorn", [
        "uvicorn",
        "main:app",
        "--host", "0.0.0.0",
        "--port", "8002",
        "--reload",
        "--log-level", "info"
    ])


if __name__ == "__main__":
    main()
