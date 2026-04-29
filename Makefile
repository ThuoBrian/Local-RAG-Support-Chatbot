.PHONY: install dev test lint typecheck clean run ingest

install:
	pip install -e .

dev:
	pip install -e ".[dev]"

test:
	pytest -m "not integration"

test-all:
	pytest

lint:
	ruff check helpdesk_rag/

typecheck:
	mypy helpdesk_rag/

clean:
	rm -rf build/ dist/ *.egg-info/ helpdesk_rag.egg-info/
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .ruff_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .mypy_cache -exec rm -rf {} + 2>/dev/null || true
	rm -rf htmlcov/ .coverage

run:
	uvicorn helpdesk_rag.app:app --reload --host 0.0.0.0 --port 8000

ingest:
	python -m helpdesk_rag.ingest