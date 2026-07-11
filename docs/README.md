# Helpdesk RAG — Technical Guide

Detailed documentation for developers and power users. For the simple user guide, see the [main README](../README.md).

## Table of contents

- [Architecture](#architecture)
- [Quick start (CLI)](#quick-start-cli)
- [Configuration](#configuration)
- [Adding documents](#adding-documents)
- [Docker](#docker)
- [Project structure](#project-structure)
- [Development](#development)
- [API reference](#api-reference)
- [Troubleshooting](#troubleshooting)

## Architecture

The system follows a modular RAG (Retrieval-Augmented Generation) architecture where each component has a single responsibility.

### System overview

```mermaid
flowchart TB
    subgraph Client
        UI[Browser UI]
    end

    subgraph FastAPI["FastAPI Server"]
        APP[app.py<br/>SSE + Sessions]
        ENGINE[RAGEngine]
        RETRIEVER[Hybrid Retriever]
        LLM[LLMClient]
    end

    subgraph Storage["Storage Layer"]
        VS[VectorStore<br/>ChromaDB]
        BM25[BM25 Index<br/>In-memory]
    end

    subgraph Ollama["Ollama (Local)"]
        EMBED[Embedding Model]
        CHAT[Chat Model]
    end

    UI -->|POST /api/chat| APP
    APP -->|prepare_stream| ENGINE
    ENGINE -->|retrieve| RETRIEVER
    RETRIEVER -->|query| VS
    RETRIEVER -->|rerank| BM25
    RETRIEVER -->|embed| EMBED
    ENGINE -->|generate_stream| LLM
    LLM -->|chat| CHAT
    APP -->|SSE events| UI
```

**Request flow:**

1. Browser sends chat message to FastAPI endpoint
2. `RAGEngine` orchestrates retrieval and generation
3. `Hybrid Retriever` finds relevant document chunks
4. `LLMClient` streams response tokens from Ollama
5. Server-sent events deliver tokens to browser in real time

### Hybrid retrieval pipeline

```text
Query ──► Embedding ──► Vector Search ──► 2× candidates
                                                   │
                      ┌────────────────────────────┘
                      ▼
              Filter by min_score
                      │
          ┌───────────┴───────────┐
          ▼                       ▼
   Vector Score (60%)      BM25 Score (40%)
          └───────────┬───────────┘
                      ▼
              Weighted Fusion
                      │
                      ▼
                Top-K Results
```

| Stage | Description |
|-------|-------------|
| **Candidate generation** | Vector similarity retrieves `top_k × 2` chunks |
| **Filtering** | Chunks below `min_score` threshold are discarded |
| **Re-ranking** | Combined score = 0.6×vector + 0.4×BM25 |

The BM25 index is built lazily on first hybrid query and cached with thread-safe locking.

### Server-sent events streaming

Real-time responses delivered via SSE with four event types:

| Event | When | Data |
|-------|------|------|
| `sources` | After retrieval | JSON array of source documents |
| `token` | Per-LLM token | JSON string (the token) |
| `error` | On failure | JSON string (error message) |
| `done` | Stream complete | Empty |

**Two-phase commit:** user messages are only saved to history after successful retrieval, preventing corrupted conversation state.

### Session management

Stateful conversations with automatic cleanup:

| Setting | Value | Purpose |
|---------|-------|---------|
| `SESSION_MAX_AGE` | 3600s | Session timeout (1 hour) |
| `MAX_SESSIONS` | 1000 | Memory cap with LRU eviction |

Background cleanup runs every 10 minutes to remove expired sessions.

### Design decisions

| Decision | Rationale |
|----------|-----------|
| **OpenAI-compatible API** | Model portability — swap Ollama for OpenAI, vLLM, etc. |
| **Lazy BM25 indexing** | Avoid startup delay; build only when needed |
| **Two-phase message commit** | Prevent corrupted history on retrieval failure |
| **Sentence-boundary truncation** | Preserve readability when context exceeds limit |
| **Incremental ingestion** | Skip existing chunks; support document updates |
| **Thread-safe BM25 cache** | Prevent race conditions during concurrent queries |

## Quick start (CLI)

### Prerequisites

- [Ollama](https://ollama.com) installed and running
- Python 3.11, 3.12, or 3.13
- [uv](https://docs.astral.sh/uv/) package manager

### 1. Pull Ollama models

```bash
ollama pull nomic-embed-text   # embedding model
ollama pull glm-5.1:cloud      # chat model (or llama3.2 for a smaller model)
```

### 2. Set up the project

```bash
uv venv --python 3.13
uv pip install -e .
```

Or use the setup script, which also copies example config and `.env` files:

```bash
./scripts/setup.sh
```

### 3. Add your documents

Place PDF, DOCX, Markdown, or TXT files in `data/documents/`:

```bash
cp /path/to/your/documents/*.pdf data/documents/
```

### 4. Ingest documents

```bash
./scripts/ingest.sh
```

This chunks your documents, generates embeddings via Ollama, and stores them in ChromaDB. Progress bars show per-file and per-batch status. Re-running ingestion skips duplicates automatically.

### 5. Start the server

Use the startup script (auto-ingests if the vector store is empty):

```bash
./scripts/start.sh
```

Or run manually:

```bash
.venv/bin/uvicorn helpdesk_rag.app:app --host 127.0.0.1 --port 8000
```

Open **http://localhost:8000** in your browser.

## Configuration

All settings live in `config/config.yaml`. You can also override any value with environment variables — env vars take precedence.

### config/config.yaml

```yaml
ollama:
  base_url: "http://localhost:11434/v1"  # Ollama OpenAI-compatible endpoint
  embedding_model: "nomic-embed-text"     # model for embeddings
  llm_model: "glm-5.1:cloud"             # model for chat generation
  temperature: 0.3                        # 0.0–2.0
  max_tokens: 768                         # max tokens per response

chunking:
  chunk_size: 1000                        # max characters per chunk
  chunk_overlap: 200                      # overlap characters between chunks

vector_store:
  persist_dir: "data/chroma"              # ChromaDB storage directory
  collection_name: "helpdesk_docs"        # collection name in ChromaDB

retrieval:
  top_k: 4                                # number of chunks to retrieve
  method: "hybrid"                        # "vector", "bm25", or "hybrid"
  min_score: 0.3                          # minimum relevance score (0.0–1.0)

chat:
  max_history_turns: 4                    # conversation turns included in prompt
  max_context_chars: 6000                 # max characters of context in prompt
```

### Environment variable overrides

| Env var | Config key | Type | Default |
|---|---|---|---|
| `OLLAMA_BASE_URL` | `ollama.base_url` | str | `http://localhost:11434/v1` |
| `OLLAMA_EMBEDDING_MODEL` | `ollama.embedding_model` | str | `nomic-embed-text` |
| `OLLAMA_LLM_MODEL` | `ollama.llm_model` | str | `glm-5.1:cloud` |
| `OLLAMA_TEMPERATURE` | `ollama.temperature` | float | `0.3` |
| `OLLAMA_MAX_TOKENS` | `ollama.max_tokens` | int | `768` |
| `CHUNK_SIZE` | `chunking.chunk_size` | int | `1000` |
| `CHUNK_OVERLAP` | `chunking.chunk_overlap` | int | `200` |
| `RETRIEVAL_TOP_K` | `retrieval.top_k` | int | `4` |
| `RETRIEVAL_MIN_SCORE` | `retrieval.min_score` | float | `0.3` |
| `MAX_CONTEXT_CHARS` | `chat.max_context_chars` | int | `6000` |
| `MAX_HISTORY_TURNS` | `chat.max_history_turns` | int | `4` |
| `HOST` | server host (uvicorn) | str | `127.0.0.1` |
| `PORT` | server port (uvicorn) | int | `8000` |

## Adding documents

Drop files into `data/documents/` and re-run ingestion:

```bash
./scripts/ingest.sh
```

Supported formats: **PDF**, **DOCX**, **Markdown** (`.md`), **plain text** (`.txt`).

Ingestion skips chunks that already exist in the vector store, so you can run it repeatedly without duplicating data.

## Docker

Build and run with Docker Compose:

```bash
docker compose -f docker/docker-compose.yml up --build
```

Or build and run manually:

```bash
docker build -t helpdesk-rag -f docker/Dockerfile .
docker run -p 8000:8000 --env-file .env -v $(pwd)/config/config.yaml:/app/config/config.yaml helpdesk-rag
```

The container runs `scripts/docker-entrypoint.sh`, which auto-ingests documents if the vector store is empty.

## Project structure

```
helpdesk_rag/              # Python source code
  app.py                   # FastAPI app with SSE streaming and session management
  config.py                # Pydantic config models with env-var overrides
  engine.py                # RAG orchestration (retrieval + LLM generation)
  retriever.py             # Hybrid / vector / BM25 retrieval with weighted re-ranking
  vector_store.py          # ChromaDB wrapper (add, query, count, get_sources)
  embeddings.py            # OpenAI-compatible embedding client for Ollama
  llm_client.py            # OpenAI-compatible LLM client (generate + stream)
  loader.py                # Multi-format document loader (PDF, DOCX, MD, TXT)
  chunker.py               # Recursive text chunker with configurable overlap
  ingest.py                # Document ingestion CLI with progress bars
  exceptions.py            # Custom exception hierarchy
  logging_config.py        # Centralized logging setup
frontend/                  # UI assets
  templates/
    index.html             # Single-page chat UI (Jinja2 template)
  static/
    css/style.css          # UI stylesheet
    js/app.js              # SSE client, Markdown rendering, session management
config/                    # Configuration files
  config.yaml              # Active configuration
  config.example.yaml      # Example configuration for new setups
  config.docker.yaml       # Docker-specific configuration
data/                      # Runtime data (contents gitignored)
  documents/               # Drop your documents here
  chroma/                  # Persisted vector store (auto-generated)
docs/                      # Additional documentation
  CODE_REVIEW.md
  README.md                # This file
scripts/                   # Automation scripts
  helpdesk.sh              # Interactive menu for non-IT users
  setup.sh                 # One-command development setup
  start.sh                 # Start the chat server
  ingest.sh                # Ingest documents
  docker-entrypoint.sh     # Docker container entrypoint
docker/                    # Docker assets
  Dockerfile
  docker-compose.yml
  .dockerignore
tests/                     # Test suite
  fixtures/                # Shared test documents
  test_*.py
```

## Development

```bash
uv pip install -e ".[dev]"   # install with dev dependencies
make test                    # run unit tests (excludes integration)
make test-all                # run all tests including integration
make lint                    # ruff linter check
make typecheck               # mypy strict type checking
make run                     # dev server with auto-reload
```

### Makefile targets

| Target | Command |
|---|---|
| `make setup` | Create venv with uv, install dev deps, copy example config |
| `make install` | `uv pip install -e .` |
| `make dev` | `uv pip install -e ".[dev]"` |
| `make lock` | Regenerate `requirements.lock` and `requirements-dev.lock` |
| `make test` | `.venv/bin/pytest -m "not integration"` |
| `make test-all` | `.venv/bin/pytest` |
| `make lint` | `.venv/bin/ruff check helpdesk_rag/` |
| `make typecheck` | `.venv/bin/mypy helpdesk_rag/` |
| `make clean` | Remove build artifacts |
| `make run` | `.venv/bin/uvicorn helpdesk_rag.app:app --reload --host 127.0.0.1` |
| `make ingest` | `./scripts/ingest.sh` |

## API reference

### `GET /`

Serves the chat UI (HTML page).

### `POST /api/chat`

Accepts a chat message and returns a streaming SSE response.

**Request body:**

```json
{
  "message": "How do I enable BitLocker?",
  "session_id": "uuid-string"
}
```

**SSE event types:**

| Event | Data | Description |
|---|---|---|
| `sources` | JSON array of source objects | Retrieved document chunks with metadata |
| `token` | JSON string | Individual generated token |
| `error` | JSON string | Error message |
| `done` | (empty) | Stream completed |

## Troubleshooting

| Problem | Solution |
|---|---|
| Ollama not responding | Start Ollama: `ollama serve` |
| Port already in use | Use a different port: `PORT=8080 ./scripts/start.sh` |
| Missing documents | Verify files are in `data/documents/` |
| Tests fail | Run `make lint`, `make typecheck`, then `make test` |
| Docker build fails | Ensure `.env` and `config/config.yaml` exist |

## License

[MIT](../LICENSE)
