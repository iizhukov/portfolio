#!/bin/bash
set -e

# optional: print environment
echo "Starting upload service..."

exec uvicorn main:app --host "${HOST:-0.0.0.0}" --port "${PORT:-8003}" --log-level info
