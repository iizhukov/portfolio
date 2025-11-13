#!/bin/sh
set -e

echo "Waiting for MinIO to be ready..."
sleep 10

export MC_HOST_minio=http://minioadmin:minioadmin@infra-minio:9000

echo "Creating buckets..."

mc mb minio/public --ignore-existing || echo "Bucket 'public' already exists"
mc mb minio/uploads --ignore-existing || echo "Bucket 'uploads' already exists"

echo "Setting bucket policies..."

mc anonymous set public minio/public || echo "Failed to set public policy for 'public' bucket"
mc anonymous set public minio/uploads || echo "Failed to set public policy for 'uploads' bucket"

echo "Created buckets:"
mc ls minio

echo "Bucket initialization completed!"