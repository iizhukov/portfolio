FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY shared/python ./shared/python
RUN pip install -e ./shared/python

COPY services/connections/requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

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
