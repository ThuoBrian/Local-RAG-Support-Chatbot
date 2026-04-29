# Helpdesk RAG

Local RAG chatbot for IT support documentation using Ollama + ChromaDB, with a FastAPI web UI and SSE streaming.

## Architecture

```
data/documents/  →  loader  →  chunker  →  embeddings (Ollama)  →  ChromaDB
                                                              ↓
user query  →  FastAPI + HTML UI  →  engine  →  retriever  →  LLM (Ollama)
                                       ↑___________________|
```

**Retrieval methods:** vector, BM25, or hybrid (default).

**Web UI:** FastAPI serves a single-page chat interface with server-sent events (SSE) for token-by-token streaming.

## Quick start

1. Install [Ollama](https://ollama.com) and pull models:
   ```bash
   ollama pull nomic-embed-text
   ollama pull glm-5.1:cloud
   ```

2. Set up the project:
   ```bash
   git clone https://github.com/ThuoBrian/Local-RAG-chatbot-for-Technology-Support.git
   cd helpdesk-rag
   python3.13 -m venv .venv
   source .venv/bin/activate
   pip install -e ".[dev]"
   ```

3. Ingest documents:
   ```bash
   python -m helpdesk_rag.ingest
   ```

4. Start the server:
   ```bash
   ./start.sh
   # or: uvicorn helpdesk_rag.app:app --reload --host 0.0.0.0 --port 8000
   ```

Open http://localhost:8000 in your browser.

## Configuration

Edit `config.yaml` or use environment variables (see `.env.example`):

| Env var | Config key | Default |
|---------|-----------|---------|
| `OLLAMA_BASE_URL` | ollama.base_url | `http://localhost:11434/v1` |
| `OLLAMA_LLM_MODEL` | ollama.llm_model | `glm-5.1:cloud` |
| `OLLAMA_EMBEDDING_MODEL` | ollama.embedding_model | `nomic-embed-text` |
| `RETRIEVAL_TOP_K` | retrieval.top_k | `4` |
| `RETRIEVAL_MIN_SCORE` | retrieval.min_score | `0.3` |
| `HOST` | server host | `0.0.0.0` |
| `PORT` | server port | `8000` |

## Adding documents

Drop PDF, DOCX, Markdown, or TXT files into `data/documents/` and re-run:
```bash
python -m helpdesk_rag.ingest
```

The ingestion script shows progress bars for file processing and embedding.

## Docker

```bash
docker build -t helpdesk-rag .
docker run -p 8000:8000 --env-file .env helpdesk-rag
```

## Development

```bash
pip install -e ".[dev]"
pytest                    # run tests
ruff check helpdesk_rag/  # lint
mypy helpdesk_rag/        # type check
make run                  # dev server with auto-reload
```

## Project structure

```
helpdesk_rag/
  app.py           # FastAPI app with SSE streaming
  config.py        # Pydantic config with validation
  engine.py        # RAG orchestration
  exceptions.py    # Custom exception hierarchy
  embeddings.py    # OpenAI-compatible embedding client
  llm_client.py    # OpenAI-compatible LLM client
  loader.py        # Document loading (PDF, DOCX, MD, TXT)
  chunker.py       # Recursive text chunker
  vector_store.py  # ChromaDB vector store
  retriever.py     # Hybrid retrieval (vector + BM25)
  ingest.py        # Document ingestion CLI with progress bars
  logging_config.py # Logging setup
templates/
  index.html       # Chat UI template
static/
  style.css        # UI styles
  app.js           # SSE client, markdown rendering
```

## License

MIT