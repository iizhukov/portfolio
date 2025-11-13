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

COPY apps/bot/pyproject.toml apps/bot/poetry.lock ./apps/bot/

WORKDIR /app/apps/bot

RUN poetry install --no-interaction --no-ansi --no-root

COPY apps/bot/ .

RUN chmod +x entrypoint.sh

FROM base AS runtime

WORKDIR /app

RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /usr/local /usr/local
COPY --from=builder /app/shared/python /app/shared/python
COPY --from=builder /app/apps/bot /app/apps/bot

RUN useradd --create-home --shell /bin/bash app \
    && chown -R app:app /app

USER app

WORKDIR /app/apps/bot

ENTRYPOINT ["./entrypoint.sh"]

