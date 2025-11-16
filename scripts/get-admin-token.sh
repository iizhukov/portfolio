#!/bin/bash

set -e

PROJECT_NAME="${COMPOSE_PROJECT_NAME:-portfolio}"

TOKEN=""

if command -v docker &> /dev/null; then
    if docker compose ps service-gateway 2>/dev/null | grep -q "Up"; then
        TOKEN=$(docker compose exec -T service-gateway cat /shared/admin/token 2>/dev/null || echo "")
    fi

    if [ -z "$TOKEN" ]; then
        VOLUME_PATH=$(docker volume inspect "${PROJECT_NAME}_admin-token" --format '{{ .Mountpoint }}' 2>/dev/null || echo "")
        if [ -n "$VOLUME_PATH" ] && [ -f "$VOLUME_PATH/token" ]; then
            TOKEN=$(cat "$VOLUME_PATH/token" 2>/dev/null || echo "")
        fi
    fi
fi

if [ -z "$TOKEN" ]; then
    echo "Error: Could not access admin token."
    exit 1
fi


echo "$TOKEN"
