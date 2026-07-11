from __future__ import annotations

import asyncio
import json
import logging
import time
from typing import Any
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field
from starlette.middleware.base import BaseHTTPMiddleware
from sse_starlette.sse import EventSourceResponse

from helpdesk_rag.config import load_config
from helpdesk_rag.engine import RAGEngine
from helpdesk_rag.exceptions import EmbeddingError, LLMError, RetrievalError, VectorStoreError
from helpdesk_rag.logging_config import setup_logging

logger = logging.getLogger(__name__)

_engine: RAGEngine | None = None
_engine_task: asyncio.Task[None] | None = None
_sessions: dict[str, list[dict[str, str]]] = {}
_session_timestamps: dict[str, float] = {}
SESSION_MAX_AGE = 3600  # 1 hour
MAX_SESSIONS = 1000


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=10000)
    session_id: str = Field(pattern=r"^[a-zA-Z0-9-]{1,128}$")


class CSPMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Any) -> Any:
        response = await call_next(request)
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; script-src 'self' cdn.jsdelivr.net; style-src 'self' 'unsafe-inline'"
        )
        return response


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    global _engine, _engine_task
    setup_logging()
    try:
        config = load_config("config.yaml")
        _engine = await asyncio.to_thread(RAGEngine, config)
        logger.info("RAG engine initialized successfully")
    except Exception:
        logger.exception("Failed to initialize RAG engine")
        raise
    _engine_task = asyncio.create_task(_cleanup_sessions())
    yield


async def _cleanup_sessions() -> None:
    while True:
        try:
            await asyncio.sleep(600)
            now = time.time()
            expired = [sid for sid, ts in _session_timestamps.items() if now - ts > SESSION_MAX_AGE]
            for sid in expired:
                _sessions.pop(sid, None)
                _session_timestamps.pop(sid, None)
            if expired:
                logger.debug("Cleaned %d expired sessions", len(expired))
            # Evict oldest sessions if over cap
            while len(_sessions) > MAX_SESSIONS:
                oldest_sid = min(_session_timestamps, key=_session_timestamps.get)  # type: ignore[arg-type]
                _sessions.pop(oldest_sid, None)
                _session_timestamps.pop(oldest_sid, None)
                logger.debug("Evicted oldest session %s (cap=%d)", oldest_sid, MAX_SESSIONS)
        except Exception:
            logger.exception("Session cleanup error")


app = FastAPI(title="Helpdesk RAG", lifespan=lifespan)
app.add_middleware(CSPMiddleware)
app.mount("/static", StaticFiles(directory="frontend/static"), name="static")
templates = Jinja2Templates(directory="frontend/templates")


@app.get("/", response_class=HTMLResponse)
async def index(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(request, "index.html")


@app.post("/api/chat")
async def chat(request: ChatRequest) -> EventSourceResponse:
    engine = _engine
    if engine is None:
        return EventSourceResponse(_error_stream("Engine failed to initialize. Please restart the server."))

    session_id = request.session_id
    now = time.time()
    _session_timestamps[session_id] = now
    if session_id not in _sessions:
        _sessions[session_id] = []
    history = _sessions[session_id]

    user_msg = {"role": "user", "content": request.message}

    async def event_stream() -> AsyncGenerator[dict[str, str], None]:
        full_answer: list[str] = []
        try:
            stream_gen, sources = await asyncio.to_thread(engine.prepare_stream, request.message, history + [user_msg])
        except (EmbeddingError, VectorStoreError, RetrievalError) as exc:
            logger.exception("Retrieval failed for query: %s", request.message[:100])
            yield {"event": "error", "data": json.dumps(f"Retrieval error: {exc}")}
            return
        except LLMError as exc:
            logger.exception("LLM failed for query: %s", request.message[:100])
            yield {"event": "error", "data": json.dumps(f"Language model error: {exc}")}
            return
        except Exception:
            logger.exception("Unexpected error for query: %s", request.message[:100])
            yield {"event": "error", "data": json.dumps("An unexpected error occurred. Please try again.")}
            return

        # Commit user message only after successful retrieval
        history.append(user_msg)

        if not sources:
            fallback = "I don't have information about this in the available documentation."
            full_answer.append(fallback)
            history.append({"role": "assistant", "content": fallback})
            yield {"event": "sources", "data": json.dumps([])}
            yield {"event": "token", "data": json.dumps(fallback)}
            yield {"event": "done", "data": ""}
            return

        yield {"event": "sources", "data": json.dumps(sources)}

        try:
            while True:
                token = await asyncio.to_thread(next, stream_gen, None)
                if token is None:
                    break
                full_answer.append(token)
                yield {"event": "token", "data": json.dumps(token)}
        except Exception:
            logger.exception("LLM stream interrupted")
            if full_answer:
                history.append({"role": "assistant", "content": "".join(full_answer)})
            yield {"event": "error", "data": json.dumps("Stream interrupted. Partial response may be shown.")}
            return

        history.append({"role": "assistant", "content": "".join(full_answer)})
        yield {"event": "done", "data": ""}

    return EventSourceResponse(event_stream())


async def _error_stream(message: str) -> AsyncGenerator[dict[str, str], None]:
    yield {"event": "error", "data": json.dumps(message)}
