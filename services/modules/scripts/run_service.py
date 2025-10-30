#!/usr/bin/env python3
import os
import sys


def main() -> None:
    host = os.getenv("HOST")
    grpc_port = os.getenv("GRPC_PORT")

    print("=" * 60)
    print("🚀 Starting Modules Service")
    print("=" * 60)
    print()
    print("Service endpoints:")
    print(f"   - gRPC: {host}:{grpc_port}")
    print()
    print("Press Ctrl+C to stop")
    print("=" * 60)
    print()

    os.execvp(sys.executable, [sys.executable, "main.py"])


if __name__ == "__main__":
    main()

