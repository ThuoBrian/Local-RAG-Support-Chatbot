#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$PROJECT_ROOT"

if [ ! -d ".venv" ]; then
    echo "Virtual environment not found. Run ./scripts/setup.sh first."
    exit 1
fi

# Ingest documents if vector store is empty
CHUNKS=$(.venv/bin/python -c "from helpdesk_rag.config import load_config; from helpdesk_rag.vector_store import VectorStore; print(VectorStore(load_config().vector_store).count())" 2>/dev/null || echo "0")
if [ "$CHUNKS" = "0" ]; then
    echo "Vector store is empty. Running ingestion..."
    .venv/bin/python -m helpdesk_rag.ingest
fi

# Start the FastAPI server
exec .venv/bin/uvicorn helpdesk_rag.app:app --host "${HOST:-127.0.0.1}" --port "${PORT:-8000}"
