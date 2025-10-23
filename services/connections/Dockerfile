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

COPY services/connections/pyproject.toml services/connections/poetry.lock* ./

RUN poetry install --no-interaction --no-ansi --no-root

COPY services/connections/ .

RUN echo "Checking for gRPC files..." && \
    ls -la generated/ && \
    if [ ! -f "generated/connections_pb2.py" ]; then \
        echo "gRPC files not found, generating..." && \
        cd scripts && python generate_grpc.py; \
    else \
        echo "gRPC files already exist"; \
    fi && \
    echo "Final check:" && \
    ls -la generated/

RUN useradd --create-home --shell /bin/bash app \
    && chown -R app:app /app
USER app

EXPOSE 8002

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8002"]
