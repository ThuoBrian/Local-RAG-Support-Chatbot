from __future__ import annotations

import asyncio
import json
import logging
import time
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from sse_starlette.sse import EventSourceResponse

from helpdesk_rag.config import load_config
from helpdesk_rag.engine import RAGEngine
from helpdesk_rag.logging_config import setup_logging

logger = logging.getLogger(__name__)

_engine: RAGEngine | None = None
_sessions: dict[str, list[dict[str, str]]] = {}
_session_timestamps: dict[str, float] = {}
SESSION_MAX_AGE = 3600  # 1 hour


class ChatRequest(BaseModel):
    message: str
    session_id: str


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    global _engine
    setup_logging()
    try:
        config = load_config("config.yaml")
        _engine = await asyncio.to_thread(RAGEngine, config)
        logger.info("RAG engine initialized successfully")
    except Exception:
        logger.exception("Failed to initialize RAG engine")
        raise
    asyncio.create_task(_cleanup_sessions())
    yield


async def _cleanup_sessions() -> None:
    while True:
        await asyncio.sleep(600)
        now = time.time()
        expired = [
            sid for sid, ts in _session_timestamps.items() if now - ts > SESSION_MAX_AGE
        ]
        for sid in expired:
            _sessions.pop(sid, None)
            _session_timestamps.pop(sid, None)
        if expired:
            logger.debug("Cleaned %d expired sessions", len(expired))


app = FastAPI(title="Helpdesk RAG", lifespan=lifespan)
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


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

    history.append({"role": "user", "content": request.message})

    async def event_stream() -> AsyncGenerator[dict[str, str], None]:
        full_answer: list[str] = []
        try:
            stream_gen, sources = await asyncio.to_thread(
                engine.prepare_stream, request.message, history
            )
        except Exception:
            logger.exception("Retrieval failed for query: %s", request.message[:100])
            history.pop()
            yield {"event": "error", "data": json.dumps("An error occurred during retrieval. Please try again.")}
            return

        if not sources:
            fallback = "I don't have information about this in the available documentation."
            full_answer.append(fallback)
            history.append({"role": "assistant", "content": fallback})
            yield {"event": "sources", "data": json.dumps([])}
            yield {"event": "token", "data": json.dumps(fallback)}
            yield {"event": "done", "data": ""}
            return

        yield {"event": "sources", "data": json.dumps(sources)}

        while True:
            token = await asyncio.to_thread(next, stream_gen, None)
            if token is None:
                break
            full_answer.append(token)
            yield {"event": "token", "data": json.dumps(token)}

        history.append({"role": "assistant", "content": "".join(full_answer)})
        yield {"event": "done", "data": ""}

    return EventSourceResponse(event_stream())


async def _error_stream(message: str) -> AsyncGenerator[dict[str, str], None]:
    yield {"event": "error", "data": json.dumps(message)}