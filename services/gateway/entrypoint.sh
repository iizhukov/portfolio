#!/bin/bash
set -e

echo "Starting gateway service..."

if [ -n "${ADMIN_TOKEN_FILE:-}" ]; then
  mkdir -p "$(dirname "${ADMIN_TOKEN_FILE}")"
fi

if [ -z "${ADMIN_API_TOKEN:-}" ]; then
  echo "Generating ADMIN_API_TOKEN..."
  ADMIN_API_TOKEN=$(python scripts/admin_token.py)
  export ADMIN_API_TOKEN
else
  echo "Using provided ADMIN_API_TOKEN."
fi

if [ -n "${ADMIN_TOKEN_FILE:-}" ] && [ -f "${ADMIN_TOKEN_FILE}" ]; then
  chmod 644 "${ADMIN_TOKEN_FILE}"
  echo "Admin API token written to ${ADMIN_TOKEN_FILE}"
fi

echo "Admin API token: ${ADMIN_API_TOKEN}"
echo "Starting uvicorn server..."
exec uvicorn main:app --host "${HOST:-0.0.0.0}" --port "${PORT:-8000}" --log-level info
