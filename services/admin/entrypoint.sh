#!/bin/bash
set -e

echo "Starting admin service..."

echo "Starting uvicorn server..."
exec uvicorn main:app --host "${HOST:-0.0.0.0}" --port "${PORT:-8004}" --log-level info
