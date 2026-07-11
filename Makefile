.PHONY: install dev test test-all lint typecheck clean run ingest setup lock

install:
	uv pip install -e .

dev:
	uv pip install -e ".[dev]"

setup:
	./scripts/setup.sh

lock:
	uv pip compile pyproject.toml -o requirements.lock
	uv pip compile pyproject.toml --extra dev -o requirements-dev.lock

test:
	.venv/bin/ruff check helpdesk_rag/
	.venv/bin/ruff format --check helpdesk_rag/
	.venv/bin/pytest -m "not integration"

test-all:
	.venv/bin/pytest

lint:
	.venv/bin/ruff check helpdesk_rag/
	.venv/bin/ruff format --check helpdesk_rag/

typecheck:
	.venv/bin/mypy helpdesk_rag/

clean:
	rm -rf build/ dist/ *.egg-info/ helpdesk_rag.egg-info/
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .ruff_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .mypy_cache -exec rm -rf {} + 2>/dev/null || true
	rm -rf htmlcov/ .coverage

run:
	.venv/bin/uvicorn helpdesk_rag.app:app --reload --host 127.0.0.1 --port 8000

ingest:
	./scripts/ingest.sh
