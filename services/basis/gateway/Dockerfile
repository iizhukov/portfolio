ARG PYTHON_BASE_IMAGE=portfolio-python-base:latest
FROM ${PYTHON_BASE_IMAGE} AS base

FROM base AS builder

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir -p /app/services/basis/gateway

WORKDIR /app/services/basis/gateway

COPY pyproject.toml poetry.lock ./

RUN poetry install --no-interaction --no-ansi --no-root

COPY . .

RUN python scripts/generate_grpc.py

RUN poetry run python scripts/generate_grpc.py && \
    set -eux; \
    required_files="connections/connections_pb2.py connections/connections_pb2_grpc.py \
        modules/modules_pb2.py modules/modules_pb2_grpc.py \
        admin/admin_pb2.py admin/admin_pb2_grpc.py"; \
    for rel in $required_files; do \
        [ -f "generated/$rel" ] || (echo "Still missing generated/$rel" && exit 1); \
    done

RUN chmod +x entrypoint.sh

FROM base AS runtime

WORKDIR /app

COPY --from=builder /usr/local /usr/local
COPY --from=builder /app/services/basis/gateway /app/services/basis/gateway

WORKDIR /app/services/basis/gateway

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

ENTRYPOINT ["./entrypoint.sh"]
