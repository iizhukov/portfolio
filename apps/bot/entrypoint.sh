#!/bin/bash
set -e

echo "Starting bot service..."

if [ -z "${ADMIN_API_TOKEN:-}" ] && [ -n "${ADMIN_TOKEN_FILE:-}" ] && [ -f "${ADMIN_TOKEN_FILE}" ]; then
  echo "Loading ADMIN_API_TOKEN from ${ADMIN_TOKEN_FILE}"
  ADMIN_API_TOKEN="$(cat "${ADMIN_TOKEN_FILE}")"
  export ADMIN_API_TOKEN
fi

export PYTHONPATH=/app/apps/bot:/app/shared/python:$PYTHONPATH

echo "Initializing database (if needed)..."
python -c "from scripts.init_db import main; main()" || echo "Database already initialized or error occurred"

echo "Starting bot..."
exec python main.py
