ARG PYTHON_BASE_IMAGE=portfolio-python-base:latest
FROM ${PYTHON_BASE_IMAGE} AS base

FROM base AS builder

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir -p /app/services/basis/modules

WORKDIR /app/services/basis/modules

COPY pyproject.toml poetry.lock ./

RUN poetry install --no-interaction --no-ansi --no-root

COPY . .

RUN poetry run python scripts/generate_grpc.py && \
    set -eux; \
    required_files="modules/modules_pb2.py modules/modules_pb2_grpc.py"; \
    for rel in $required_files; do \
        [ -f "generated/$rel" ] || (echo "Still missing generated/$rel" && exit 1); \
    done

RUN chmod +x entrypoint.sh

FROM base AS runtime

WORKDIR /app

COPY --from=builder /usr/local /usr/local
COPY --from=builder /app/services/basis/modules /app/services/basis/modules

RUN useradd --create-home --shell /bin/bash app \
    && chown -R app:app /app

USER app

WORKDIR /app/services/basis/modules

EXPOSE 50051 8001

ENTRYPOINT ["./entrypoint.sh"]

