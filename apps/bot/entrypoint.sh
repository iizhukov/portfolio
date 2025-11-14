#!/bin/bash
set -e

echo "Starting bot service..."

export PYTHONPATH=/app/apps/bot:/app/shared/python:$PYTHONPATH

echo "Initializing database (if needed)..."
python -c "from scripts.init_db import main; main()" || echo "Database already initialized or error occurred"

echo "Starting bot..."
exec python main.py
