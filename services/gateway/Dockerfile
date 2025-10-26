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

COPY services/gateway/pyproject.toml ./services/gateway/
COPY services/gateway/poetry.lock* ./services/gateway/
COPY services/gateway/ ./services/gateway/

WORKDIR /app/services/gateway

RUN poetry install --no-interaction --no-ansi --no-root

RUN echo "Checking for gRPC files..." && \
    if [ ! -f "generated/connections_pb2.py" ]; then \
        echo "gRPC files not found, generating..." && \
        python scripts/generate_grpc.py; \
    else \
        echo "gRPC files already exist"; \
    fi

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
