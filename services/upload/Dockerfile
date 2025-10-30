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

COPY services/upload/pyproject.toml ./services/upload/
COPY services/upload/poetry.lock* ./services/upload/
COPY services/upload ./services/upload

WORKDIR /app/services/upload

RUN poetry install --no-interaction --no-ansi --no-root

COPY services/upload/entrypoint.sh ./entrypoint.sh
RUN chmod +x ./entrypoint.sh

EXPOSE 8003

ENTRYPOINT ["./entrypoint.sh"]
