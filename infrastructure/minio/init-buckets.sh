#!/bin/sh
set -e

echo "Waiting for MinIO to be ready..."
sleep 10

MINIO_ROOT_USER="${MINIO_ROOT_USER:-minioadmin}"
MINIO_ROOT_PASSWORD="${MINIO_ROOT_PASSWORD:-minioadmin}"

export MC_HOST_minio="http://${MINIO_ROOT_USER}:${MINIO_ROOT_PASSWORD}@infra-minio:9000"

echo "Configuring MinIO client..."
mc alias set minio http://infra-minio:9000 "${MINIO_ROOT_USER}" "${MINIO_ROOT_PASSWORD}" || {
    echo "Failed to configure MinIO client"
    exit 1
}

echo "Creating buckets..."

mc mb minio/public --ignore-existing || echo "Bucket 'public' already exists"
mc mb minio/uploads --ignore-existing || echo "Bucket 'uploads' already exists"

echo "Setting bucket policies..."

mc anonymous set public minio/public || {
    echo "Warning: Failed to set public policy for 'public' bucket, trying alternative method..."
    mc anonymous set download minio/public || echo "Could not set public policy for 'public' bucket"
}

mc anonymous set public minio/uploads || {
    echo "Warning: Failed to set public policy for 'uploads' bucket, trying alternative method..."
    mc anonymous set download minio/uploads || echo "Could not set public policy for 'uploads' bucket"
}

echo "Verifying bucket policies..."
echo "Public bucket policy:"
mc anonymous get minio/public || echo "Could not get policy for 'public' bucket"
echo "Uploads bucket policy:"
mc anonymous get minio/uploads || echo "Could not get policy for 'uploads' bucket"

echo "Created buckets:"
mc ls minio

echo "Bucket initialization completed!"