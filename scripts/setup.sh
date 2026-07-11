#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$PROJECT_ROOT"

if ! command -v uv >/dev/null 2>&1; then
    echo "uv not found. Installing uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
fi

if [ ! -d ".venv" ]; then
    echo "Creating virtual environment with uv..."
    uv venv --python 3.13
fi

echo "Installing package with dev dependencies..."
uv pip install -r requirements-dev.lock

mkdir -p data/documents data/chroma

if [ ! -f "config/config.yaml" ]; then
    echo "Creating config/config.yaml from example..."
    cp config/config.example.yaml config/config.yaml
fi

if [ ! -f ".env" ]; then
    echo "Creating .env from example..."
    cp .env.example .env
fi

echo "Setup complete. Add documents to data/documents/, then run ./scripts/ingest.sh"
