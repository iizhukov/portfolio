#!/bin/bash
set -e

echo "Starting bot service..."

export PYTHONPATH=/app/apps/bot:/app/shared/python:$PYTHONPATH

echo "Initializing database (if needed)..."
python scripts/init_db.py || echo "Database already initialized or error occurred"

echo "Starting bot..."
exec python main.py
