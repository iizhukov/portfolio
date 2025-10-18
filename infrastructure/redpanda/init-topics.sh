#!/bin/bash
set -e

echo "Waiting for Redpanda to be ready..."
sleep 30

echo "Creating infrastructure topics..."

rpk topic create admin_events --partitions 1 --replicas 1 || echo "Topic admin_events already exists"

echo "Infrastructure topics created:"
rpk topic list

echo "Infrastructure topic initialization completed!"
