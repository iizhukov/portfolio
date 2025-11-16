ARG PYTHON_BASE_IMAGE=portfolio-python-base:latest
FROM ${PYTHON_BASE_IMAGE} AS base

FROM base AS builder

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir -p /app/services/projects

WORKDIR /app/services/projects

COPY pyproject.toml poetry.lock ./

RUN poetry install --no-interaction --no-ansi --no-root

COPY . .

RUN poetry run python scripts/generate_grpc.py && \
    set -eux; \
    required_files="projects/projects_pb2.py projects/projects_pb2_grpc.py \
        modules/modules_pb2.py modules/modules_pb2_grpc.py"; \
    for rel in $required_files; do \
        [ -f "generated/$rel" ] || (echo "Still missing generated/$rel" && exit 1); \
    done

RUN chmod +x entrypoint.sh

FROM base AS runtime

WORKDIR /app

COPY --from=builder /usr/local /usr/local
COPY --from=builder /app/services/projects /app/services/projects

RUN useradd --create-home --shell /bin/bash app \
    && chown -R app:app /app

USER app

WORKDIR /app/services/projects

EXPOSE 8004 50054

ENTRYPOINT ["./entrypoint.sh"]

