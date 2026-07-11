#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$PROJECT_ROOT"

# Ingest documents if vector store is empty
CHUNKS=$(uv run python -c "from helpdesk_rag.config import load_config; from helpdesk_rag.vector_store import VectorStore; print(VectorStore(load_config().vector_store).count())" 2>/dev/null || echo "0")
if [ "$CHUNKS" = "0" ]; then
    echo "Vector store is empty. Running ingestion..."
    uv run python -m helpdesk_rag.ingest
fi

# Start the FastAPI server
exec uv run uvicorn helpdesk_rag.app:app --host "${HOST:-127.0.0.1}" --port "${PORT:-8000}"
