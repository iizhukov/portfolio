ARG PYTHON_BASE_IMAGE=portfolio-python-base:latest
FROM ${PYTHON_BASE_IMAGE} AS base

FROM base AS builder

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir -p /app/services/connections

WORKDIR /app/services/connections

COPY pyproject.toml poetry.lock ./

RUN poetry install --no-interaction --no-ansi --no-root

COPY . .

RUN poetry run python scripts/generate_grpc.py && \
    set -eux; \
    required_files="connections/connections_pb2.py connections/connections_pb2_grpc.py \
        modules/modules_pb2.py modules/modules_pb2_grpc.py"; \
    for rel in $required_files; do \
        [ -f "generated/$rel" ] || (echo "Still missing generated/$rel" && exit 1); \
    done

RUN chmod +x entrypoint.sh

FROM base AS runtime

WORKDIR /app

COPY --from=builder /usr/local /usr/local
COPY --from=builder /app/services/connections /app/services/connections

RUN useradd --create-home --shell /bin/bash app \
    && chown -R app:app /app

USER app

WORKDIR /app/services/connections

EXPOSE 8002 50052

ENTRYPOINT ["./entrypoint.sh"]
