#!/bin/bash
set -e

echo "Starting modules service..."

echo "Initializing database (if needed)..."
python -c "from scripts.init_db import main; main()" || echo "Database already initialized or error occurred"

echo "Launching Modules HTTP/gRPC service..."
exec uvicorn main:app --host "${HOST:-0.0.0.0}" --port "${PORT:-8001}" --log-level info

