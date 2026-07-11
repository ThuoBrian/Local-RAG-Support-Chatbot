FROM python:3.13-slim AS builder

WORKDIR /app

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml .
COPY helpdesk_rag/ helpdesk_rag/
COPY requirements.lock .
COPY requirements-dev.lock .

RUN uv venv --python 3.13 && \
    uv pip install --system -r requirements.lock -e .

FROM python:3.13-slim

WORKDIR /app

COPY --from=builder /usr/local/lib/python3.13/site-packages /usr/local/lib/python3.13/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
COPY --from=builder /app /app
COPY --from=builder /usr/local/bin/uvicorn /usr/local/bin/uvicorn

COPY config/ config/
COPY frontend/ frontend/
COPY scripts/docker-entrypoint.sh .
RUN chmod +x docker-entrypoint.sh

EXPOSE 8000

CMD ["./docker-entrypoint.sh"]
