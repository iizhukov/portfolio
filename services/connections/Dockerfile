FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install poetry==1.8.3

RUN poetry config virtualenvs.create false

COPY shared/python ./shared/python
RUN cd shared/python && poetry install --no-interaction --no-ansi

COPY services/connections/pyproject.toml ./services/connections/
COPY services/connections/poetry.lock* ./services/connections/
COPY services/connections/ ./services/connections/

WORKDIR /app/services/connections

RUN poetry install --no-interaction --no-ansi --no-root

RUN set -eux; \
    required_files="connections/connections_pb2.py \
        connections/connections_pb2_grpc.py \
        connections/connections_pb2.pyi \
        modules/modules_pb2.py \
        modules/modules_pb2_grpc.py \
        modules/modules_pb2.pyi"; \
    missing=0; \
    for rel in $required_files; do \
        if [ ! -f "generated/$rel" ]; then \
            echo "Missing generated/$rel"; \
            missing=1; \
        fi; \
    done; \
    if [ "$missing" -eq 1 ]; then \
        echo "Generating gRPC files..."; \
        python scripts/generate_grpc.py; \
    else \
        echo "All gRPC files already present"; \
    fi; \
    for rel in $required_files; do \
        [ -f "generated/$rel" ] || (echo "Still missing generated/$rel" && exit 1); \
    done; \
    ls -la generated/

COPY services/connections/entrypoint.sh ./services/connections/entrypoint.sh
RUN chmod +x ./services/connections/entrypoint.sh

RUN useradd --create-home --shell /bin/bash app \
    && chown -R app:app /app
USER app

WORKDIR /app/services/connections

EXPOSE 8002 50051

ENTRYPOINT ["./entrypoint.sh"]
