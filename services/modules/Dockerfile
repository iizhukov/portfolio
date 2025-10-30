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

COPY services/modules/pyproject.toml ./services/modules/
COPY services/modules/poetry.lock* ./services/modules/
COPY services/modules ./services/modules

WORKDIR /app/services/modules

RUN poetry install --no-interaction --no-ansi --no-root

RUN set -eux; \
    required_files="modules/modules_pb2.py modules/modules_pb2_grpc.py modules/modules_pb2.pyi"; \
    missing=0; \
    for rel in $required_files; do \
        if [ ! -f "generated/$rel" ]; then \
            echo "Missing generated/$rel"; \
            missing=1; \
        fi; \
    done; \
    if [ "$missing" -eq 1 ]; then \
        python scripts/generate_grpc.py; \
    else \
        echo "All gRPC files already present"; \
    fi; \
    for rel in $required_files; do \
        [ -f "generated/$rel" ] || (echo "Still missing generated/$rel" && exit 1); \
    done

COPY services/modules/entrypoint.sh ./entrypoint.sh
RUN chmod +x ./entrypoint.sh

EXPOSE 50051 8001

ENTRYPOINT ["./entrypoint.sh"]

