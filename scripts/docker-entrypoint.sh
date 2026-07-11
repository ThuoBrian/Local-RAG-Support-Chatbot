#!/usr/bin/env bash
set -euo pipefail

cd /app

# Ingest documents if vector store is empty
CHUNKS=$(.venv/bin/python -c "from helpdesk_rag.config import load_config; from helpdesk_rag.vector_store import VectorStore; print(VectorStore(load_config().vector_store).count())" 2>/dev/null || echo "0")
if [ "$CHUNKS" = "0" ]; then
    echo "Vector store is empty. Running ingestion..."
    .venv/bin/python -m helpdesk_rag.ingest
fi

# Start the FastAPI server
exec .venv/bin/uvicorn helpdesk_rag.app:app --host "${HOST:-0.0.0.0}" --port "${PORT:-8000}"
