FROM python:3.12-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

FROM base AS builder

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir poetry==1.8.3
RUN poetry config virtualenvs.create false

COPY shared/python ./shared/python
RUN cd shared/python && poetry install --no-interaction --no-ansi

COPY services/gateway/pyproject.toml services/gateway/poetry.lock ./services/gateway/

WORKDIR /app/services/gateway

RUN poetry install --no-interaction --no-ansi --no-root

COPY services/gateway/ .

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

RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /usr/local /usr/local
COPY --from=builder /app/shared/python /app/shared/python
COPY --from=builder /app/services/gateway /app/services/gateway

RUN useradd --create-home --shell /bin/bash app \
    && chown -R app:app /app

USER app

WORKDIR /app/services/gateway

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

ENTRYPOINT ["./entrypoint.sh"]
