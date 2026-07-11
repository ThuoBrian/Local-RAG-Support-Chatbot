#!/usr/bin/env bash
set -euo pipefail

cd /app

# Ingest documents if vector store is empty
CHUNKS=$(uv run python -c "from helpdesk_rag.config import load_config; from helpdesk_rag.vector_store import VectorStore; print(VectorStore(load_config().vector_store).count())" 2>/dev/null || echo "0")
if [ "$CHUNKS" = "0" ]; then
    echo "Vector store is empty. Running ingestion..."
    uv run python -m helpdesk_rag.ingest
fi

# Start the FastAPI server
exec uv run uvicorn helpdesk_rag.app:app --host "${HOST:-0.0.0.0}" --port "${PORT:-8000}"
