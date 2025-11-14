#!/bin/bash
set -e

echo "Starting Projects Service..."

echo "Initializing database (if needed)..."
python -c "from scripts.init_db import main; main()" || echo "Database already initialized or error occurred"

echo "Starting service..."
exec python -m uvicorn main:app --host ${HOST} --port ${PORT}

