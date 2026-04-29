# Code Review — Helpdesk RAG

Priority-ranked findings from a senior-level code review. Each item includes the file, line range, and a concrete fix.

---

## P0 — Fix Immediately

### 1. XSS via `marked.parse()` with `innerHTML`
- **File**: `static/app.js` — lines 105, 247, 262
- **Problem**: `bubble.innerHTML = marked.parse(content)` renders raw HTML from LLM output. If the model or source documents contain `<script>` or `<img onerror=...>`, it executes in the browser.
- **Fix**: Add DOMPurify (`<script src="https://cdn.jsdelivr.net/npm/dompurify/dist/purify.min.js">`) and change to `bubble.innerHTML = DOMPurify.sanitize(marked.parse(content))`.

### 2. CDN script has no version pin or SRI hash
- **File**: `templates/index.html` — line 11
- **Problem**: `marked.min.js` is loaded from `cdn.jsdelivr.net` without a version pin or `integrity` attribute. A compromised CDN or malicious package update would execute arbitrary JS in every user's browser.
- **Fix**: Pin the version and add SRI: `<script src="https://cdn.jsdelivr.net/npm/marked@9.1.6/marked.min.js" integrity="sha384-..." crossorigin="anonymous"></script>`.

### 3. No input validation on chat endpoint
- **File**: `helpdesk_rag/app.py` — line 29
- **Problem**: `ChatRequest` has no length constraints on `message` or `session_id`. Unbounded messages waste LLM tokens and memory; unlimited session IDs exhaust the in-memory session dict.
- **Fix**: Add Pydantic constraints: `message: str = Field(min_length=1, max_length=10000)` and `session_id: str = Field(pattern=r'^[a-zA-Z0-9-]{1,128}$')`.

### 4. No CSRF protection on `POST /api/chat`
- **File**: `helpdesk_rag/app.py` — line 74
- **Problem**: Any origin can POST to `/api/chat`. A malicious site could trigger LLM requests on behalf of a user.
- **Fix**: Validate the `Origin` header against an allowlist, or require a custom `X-Requested-With` header that browsers only send for same-origin AJAX.

### 5. Unhandled errors in SSE stream loop
- **File**: `helpdesk_rag/app.py` — lines 111-116
- **Problem**: Only `prepare_stream()` is wrapped in try/except. If the LLM disconnects mid-stream, the error propagates unhandled, crashing the SSE connection with no error event sent to the client.
- **Fix**: Wrap the `while True` stream loop in try/except and yield an error event before breaking.

### 6. BM25 crashes on empty candidate list in hybrid mode
- **File**: `helpdesk_rag/retriever.py` — lines 69-71, 101-103
- **Problem**: When all vector results fall below `min_score`, `_hybrid_rerank()` receives an empty list and passes it to `BM25Okapi([])`, which raises `ZeroDivisionError`.
- **Fix**: Return early from `_hybrid_rerank` if `candidates` is empty, or filter in `retrieve()` before calling it.

---

## P1 — Fix Before Next Release

### 7. Unbounded in-memory session storage (memory leak / DoS)
- **File**: `helpdesk_rag/app.py` — lines 24-25
- **Problem**: `_sessions` and `_session_timestamps` grow without bound. Each unique `session_id` creates a new entry. A client cycling UUIDs can exhaust memory.
- **Fix**: Add an LRU cap (e.g., max 1000 sessions). Evict the oldest when the cap is exceeded.

### 8. Embedding batch sends all chunks in one API call
- **File**: `helpdesk_rag/ingest.py` — lines 57-68
- **Problem**: `tqdm([texts])` wraps a single-element list — the loop runs once, sending all chunks in one request. Large documents will timeout or exceed API limits.
- **Fix**: Split texts into batches of 64-128 and embed each batch separately. Add try/except around the embedding call so one failed document doesn't crash the entire ingestion.

### 9. Session cleanup task is fire-and-forget
- **File**: `helpdesk_rag/app.py` — line 45
- **Problem**: `asyncio.create_task(_cleanup_sessions())` discards the task reference. If the coroutine raises, the exception is silently swallowed and cleanup stops permanently.
- **Fix**: Store the task, add try/except inside the loop with logging, and add a done-callback that logs exceptions.

### 10. Broad `except Exception` catches all domain errors identically
- **File**: `helpdesk_rag/app.py` — line 94
- **Problem**: `EmbeddingError`, `VectorStoreError`, `LLMError` all produce the same generic "An error occurred" message. Different error types should give different feedback.
- **Fix**: Catch `HelpdeskRAGError` specifically. Return different SSE error messages for retrieval failures vs. LLM failures.

### 11. LLM stream errors propagate as raw exceptions
- **File**: `helpdesk_rag/llm_client.py` — lines 53-55
- **Problem**: Only stream creation is wrapped in try/except. Chunk iteration has no error handling — a network timeout mid-stream crashes the SSE connection.
- **Fix**: Wrap the `for chunk in stream` loop in try/except, catching OpenAI API errors and raising `LLMError`.

### 12. Env var type coercion has no error context
- **File**: `helpdesk_rag/config.py` — line 143
- **Problem**: `int("abc")` from `RETRIEVAL_TOP_K=abc` raises `ValueError` with no indication of which env var failed.
- **Fix**: Wrap coercion in try/except and raise `ConfigError` with the env var name and invalid value.

### 13. `start.sh` / `ingest.sh` assume `.venv` exists
- **File**: `start.sh` line 8, `ingest.sh` line 7
- **Problem**: `source .venv/bin/activate` fails with a cryptic error if `.venv` doesn't exist. The Docker image installs globally, so `start.sh` fails inside Docker.
- **Fix**: Add a guard: `if [ -d .venv ]; then source .venv/bin/activate; fi`.

### 14. No Content-Security-Policy header
- **File**: `helpdesk_rag/app.py`
- **Problem**: No CSP header is set. Combined with issue #1, this means XSS payloads can load external scripts freely.
- **Fix**: Add middleware: `Content-Security-Policy: default-src 'self'; script-src 'self' cdn.jsdelivr.net; style-src 'self' 'unsafe-inline'`.

---

## P2 — Fix When Convenient

### 15. Trailing chunk merge can exceed `chunk_size`
- **File**: `helpdesk_rag/chunker.py` — lines 73-75
- **Problem**: Small trailing chunks are merged into the previous chunk, potentially producing chunks larger than `chunk_size`.
- **Fix**: Only merge if combined size <= `chunk_size`, or document that `chunk_size` is a soft limit.

### 16. Thread safety of BM25 cache under concurrent access
- **File**: `helpdesk_rag/retriever.py` — lines 47-49, 90-99
- **Problem**: `_bm25` and related attributes are read/written without locking. `asyncio.to_thread()` runs retrieval in a thread pool, creating a data race.
- **Fix**: Add a `threading.Lock` around the BM25 check-and-rebuild logic.

### 17. `renderSources` is 64 lines of dead code
- **File**: `static/app.js` — lines 132-195
- **Problem**: The function is defined but never called. A comment says "Sources panel removed."
- **Fix**: Delete it entirely.

### 18. `innerHTML = ""` destroys the `emptyState` DOM reference
- **File**: `static/app.js` — lines 65-75
- **Problem**: `messagesEl.innerHTML = ""` destroys all children including `emptyState`. The later `appendChild(emptyState)` re-attaches a detached node, which works in most browsers but is fragile.
- **Fix**: Use `while (messagesEl.firstChild) messagesEl.removeChild(messagesEl.firstChild)` or recreate the empty state element.

### 19. Session history grows unbounded within a single session
- **File**: `helpdesk_rag/app.py` — lines 83-118
- **Problem**: Every message is appended with no cap. A long session accumulates the full conversation in memory.
- **Fix**: Cap `history` to the last N messages (e.g., 2 × `max_history_turns`).

### 20. History inconsistency on mid-stream failure
- **File**: `helpdesk_rag/app.py` — lines 86, 118
- **Problem**: The user message is appended to history before the LLM call. If the stream fails or the client disconnects, the history has the user message but no assistant response.
- **Fix**: Only commit the user message after the assistant response completes, or rollback on failure.

### 21. `VectorStore.add_chunks` loads all IDs for dedup
- **File**: `helpdesk_rag/vector_store.py` — line 64
- **Problem**: `self.collection.get()["ids"]` loads every existing ID into memory. For large stores, this is O(n).
- **Fix**: Use `collection.get(ids=new_chunk_ids)` to check only the IDs being added, or switch to upsert semantics.

### 22. BM25 index rebuilds on every chunk count change
- **File**: `helpdesk_rag/retriever.py` — lines 90-99
- **Problem**: Any ingestion triggers a full BM25 rebuild on the next query. For large corpora, this causes a latency spike.
- **Fix**: Cache with a TTL or version number. Consider building in a background thread.

### 23. SSE buffer drops last incomplete line at stream end
- **File**: `static/app.js` — lines 226-227
- **Problem**: If the final SSE `data:` line arrives without a trailing newline, `buffer` retains it but never processes it. The last token or `done` event could be lost.
- **Fix**: After the read loop, process remaining buffer content if it starts with `data: `.

### 24. `json.dumps` wrapping of SSE string events
- **File**: `helpdesk_rag/app.py` — lines 97, 105, 116
- **Problem**: `json.dumps("string")` adds extra quotes. It works because `JSON.parse()` on the client unwraps them, but it's fragile with special characters.
- **Fix**: Use a consistent approach — either send structured JSON objects for all events, or avoid `json.dumps` for plain strings.

### 25. No rate limiting on `/api/chat`
- **File**: `helpdesk_rag/app.py`
- **Problem**: Each request triggers embedding + LLM inference. No rate limiting means an attacker can exhaust GPU/CPU resources.
- **Fix**: Add rate limiting (e.g., `slowapi`) — at minimum per-IP and per-session.

### 26. User content not delimited in prompt template
- **File**: `helpdesk_rag/engine.py` — lines 121-131
- **Problem**: User messages are interpolated directly into the LLM prompt. A message like `"Ignore all previous instructions"` could manipulate the model.
- **Fix**: Wrap user content in delimiters (e.g., `<user_message>...</user_message>`) so the model can distinguish data from instructions.

---

## P3 — Nice to Have

### 27. Module-level mutable globals make testing hard
- **File**: `helpdesk_rag/app.py` — lines 23-25
- **Fix**: Move `_engine`, `_sessions`, `_session_timestamps` into an `AppState` class or use FastAPI dependency injection.

### 28. `RAGEngine.__init__` creates all dependencies concretely
- **File**: `helpdesk_rag/engine.py` — lines 56-63
- **Fix**: Accept `EmbeddingClient`, `VectorStore`, `Retriever`, `LLMClient` as constructor parameters with defaults for easier testing.

### 29. `answer()` returns an untyped dict
- **File**: `helpdesk_rag/engine.py` — lines 91-96
- **Fix**: Define a `TypedDict` or Pydantic model for the return type.

### 30. `EmbeddingClient` and `LLMClient` create separate OpenAI clients
- **Files**: `helpdesk_rag/embeddings.py` line 26, `helpdesk_rag/llm_client.py` line 18
- **Fix**: Share a single `OpenAI` client instance for connection pooling.

### 31. `logging.basicConfig` is a no-op if handlers already exist
- **File**: `helpdesk_rag/logging_config.py` — lines 7-13
- **Fix**: Use `dictConfig` or explicitly remove existing handlers before configuring.

### 32. Invalid log level silently defaults to `INFO`
- **File**: `helpdesk_rag/logging_config.py` — line 9
- **Fix**: Validate the level string and raise `ConfigError` on invalid values.

### 33. `getattr(logging, level.upper(), logging.INFO)` silently defaults on invalid level
- **File**: `helpdesk_rag/logging_config.py` — line 9
- **Fix**: Use `logging._nameToLevel` or validate against known levels.

### 34. No `aria-label` on send button or suggestion chips
- **File**: `templates/index.html` — line 55
- **Fix**: Add `aria-label="Send message"` to the button and labels to chips.

### 35. `test_chunker.py` uses `__import__("pytest")`
- **File**: `tests/test_chunker.py` — line 44
- **Fix**: Replace with a proper `import pytest` at the top.

### 36. Content preservation test is too weak
- **File**: `tests/test_chunker.py` — lines 31-39
- **Fix**: Verify total character count across chunks is within a reasonable range of the original.

### 37. `Makefile run` binds to `0.0.0.0`
- **File**: `Makefile` — line 29
- **Fix**: Use `--host 127.0.0.1` for the dev target. Only use `0.0.0.0` in production.

### 38. CSS `!important` overrides in `.error-bubble`
- **File**: `static/style.css` — lines 499-503
- **Fix**: Use higher-specificity selectors instead.

### 39. `config.yaml` baked into Docker image
- **File**: `Dockerfile` — line 22
- **Fix**: Mount config at runtime via Docker volume, or rely on environment variables.

---

## Testing Gaps

| Module | Status | Priority |
|---|---|---|
| `app.py` (endpoints, SSE, sessions) | **No tests** | P1 |
| `retriever.py` (hybrid, BM25, re-ranking) | **No tests** | P1 |
| `vector_store.py` (query, dedup, scoring) | **No tests** | P1 |
| `engine.py` (RAGEngine class methods) | Private helpers only | P2 |
| `embeddings.py` / `llm_client.py` | **No tests** | P2 |
| `ingest.py` (pipeline, batching) | **No tests** | P2 |
| `loader.py` (PDF, DOCX) | TXT/MD only | P3 |
| `exceptions.py` | Weak assertions | P3 |

---

## Summary

| Priority | Count | Focus |
|---|---|---|
| **P0** | 6 | XSS, input validation, crashes |
| **P1** | 8 | Memory leaks, error handling, security headers |
| **P2** | 12 | Dead code, race conditions, consistency |
| **P3** | 13 | Design improvements, accessibility, testing |