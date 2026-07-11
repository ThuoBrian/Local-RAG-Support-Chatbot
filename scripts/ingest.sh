#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$PROJECT_ROOT"

if [ ! -d ".venv" ]; then
    echo "Virtual environment not found."
    echo "Run ./scripts/setup.sh first, or use the interactive menu: ./scripts/helpdesk.sh"
    exit 1
fi

.venv/bin/python -m helpdesk_rag.ingest
