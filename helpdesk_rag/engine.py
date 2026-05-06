from __future__ import annotations

import logging
from collections.abc import Generator
from typing import TypedDict

from helpdesk_rag.config import RAGConfig
from helpdesk_rag.embeddings import EmbeddingClient
from helpdesk_rag.llm_client import LLMClient
from helpdesk_rag.retriever import Retriever
from helpdesk_rag.vector_store import VectorStore

logger = logging.getLogger(__name__)

CONTENT_SNIPPET_LENGTH = 500

SYSTEM_PROMPT = """\
You are an IT support knowledge assistant. Answer questions using ONLY the provided document excerpts below.

RULES:
1. Only use information from the provided context. If the context does not contain the answer, say: "I don't have information about this in the available documentation."
2. For step-by-step procedures, list the steps exactly as documented. Do not add, remove, or reorder steps.
3. If documents give conflicting information, present both alternatives clearly.
4. Be concise and direct. Use technical IT terminology as it appears in the documents.
5. For greetings or casual conversation, respond naturally.
6. Write in a natural, human tone. Do not mention source filenames, section headings, or document references in your response."""

USER_PROMPT_TEMPLATE = """\
## Relevant Documents

{context}

---

## Conversation History

{history}

---

## Current Question

<user_message>
{question}
</user_message>

Please answer the question using the relevant documents above."""


class SourceInfo(TypedDict):
    source: str
    section: str
    score: float
    content_snippet: str


class RAGEngine:
    def __init__(self, config: RAGConfig) -> None:
        self.chat_config = config.chat

        embedding_client = EmbeddingClient(config.ollama)
        vector_store = VectorStore(config.vector_store)

        self.retriever = Retriever(vector_store, embedding_client, config.retrieval)
        self.llm = LLMClient(config.ollama)

    def _prepare(self, question: str, history: list[dict[str, str]] | None = None) -> tuple[list[SourceInfo], str]:
        """Shared retrieval + context formatting + prompt building."""
        chunks = self.retriever.retrieve(question)
        if not chunks:
            return [], ""

        sources: list[SourceInfo] = [
            {
                "source": c.source,
                "section": c.section,
                "score": round(c.score, 3),
                "content_snippet": c.content[:CONTENT_SNIPPET_LENGTH],
            }
            for c in chunks
        ]

        context = self.retriever.format_context(chunks)
        context = _truncate_context(context, self.chat_config.max_context_chars)

        history_text = _format_history(history, self.chat_config.max_history_turns)
        user_prompt = USER_PROMPT_TEMPLATE.format(
            context=context,
            history=history_text,
            question=question,
        )
        logger.debug("Prepared prompt: %d chars context, %d sources", len(context), len(sources))
        return sources, user_prompt

    def answer(self, question: str, history: list[dict[str, str]] | None = None) -> dict[str, str | list[SourceInfo]]:
        sources, user_prompt = self._prepare(question, history)
        if not sources:
            return {"answer": "Seems like I don't have information about this in my model"
            ".", "sources": []}
        answer = self.llm.generate(SYSTEM_PROMPT, user_prompt)
        return {"answer": answer, "sources": sources}

    def prepare_stream(
        self, question: str, history: list[dict[str, str]] | None = None
    ) -> tuple[Generator[str, None, None], list[SourceInfo]]:
        sources, user_prompt = self._prepare(question, history)
        if not sources:
            return (t for t in ["Seems like I don't have information about this in my model."
            ]), []
        stream = self.llm.generate_stream(SYSTEM_PROMPT, user_prompt)
        return stream, sources

    def retrieve_and_format(
        self, question: str, history: list[dict[str, str]] | None = None
    ) -> tuple[list[SourceInfo], str]:
        return self._prepare(question, history)


def _truncate_context(context: str, max_chars: int) -> str:
    """Truncate context at a sentence or line boundary."""
    if len(context) <= max_chars:
        return context
    truncated = context[:max_chars]
    for sep in ("\n", ". ", "! ", "? "):
        idx = truncated.rfind(sep)
        if idx > max_chars * 0.5:
            return truncated[: idx + len(sep)]
    return truncated


def _format_history(history: list[dict[str, str]] | None, max_turns: int) -> str:
    if not history:
        return "(No previous conversation)"
    recent = history[-(max_turns * 2) :]
    lines: list[str] = []
    for msg in recent:
        role = msg.get("role", "user")
        content = msg.get("content", "")
        label = "User" if role in ("user", "human") else "Assistant"
        lines.append(f"{label}: {content}")
    return "\n".join(lines) if lines else "(No previous conversation)"
