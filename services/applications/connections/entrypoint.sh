#!/bin/bash
set -e

echo "Starting connections service..."

echo "Initializing database..."
python -c "from scripts.init_db import main; main()" || echo "Database already initialized or error occurred"

echo "Starting uvicorn server..."
exec uvicorn main:app --host 0.0.0.0 --port 8002
