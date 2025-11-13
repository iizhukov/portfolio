#!/bin/bash
set -e

echo "Starting gateway service..."

echo "Starting uvicorn server..."
exec uvicorn main:app --host "${HOST:-0.0.0.0}" --port "${PORT:-8000}" --log-level info
