#!/bin/bash
set -e

echo "Starting modules service..."

echo "Initializing database (if needed)..."
python -c "from scripts.init_db import main; main()" || echo "Database already initialized or error occurred"

echo "Launching gRPC server..."
exec python main.py

