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

RUN echo "Checking for gRPC files..." && \
    if [ ! -f "generated/connections_pb2.py" ]; then \
        echo "gRPC files not found, generating..." && \
        python scripts/generate_grpc.py; \
    else \
        echo "gRPC files already exist"; \
    fi && \
    echo "Final check:" && \
    ls -la generated/

COPY services/connections/entrypoint.sh ./services/connections/entrypoint.sh
RUN chmod +x ./services/connections/entrypoint.sh

RUN useradd --create-home --shell /bin/bash app \
    && chown -R app:app /app
USER app

WORKDIR /app/services/connections

EXPOSE 8002 50051

ENTRYPOINT ["./entrypoint.sh"]
