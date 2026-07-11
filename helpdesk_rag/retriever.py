from __future__ import annotations

import logging
import re
import threading
from dataclasses import dataclass
from typing import Any

from rank_bm25 import BM25Okapi  # type: ignore[import-untyped]

from helpdesk_rag.config import RetrievalConfig
from helpdesk_rag.embeddings import EmbeddingClient
from helpdesk_rag.vector_store import QueryResult, VectorStore

logger = logging.getLogger(__name__)

VECTOR_WEIGHT = 0.6
BM25_WEIGHT = 0.4

_STOP_WORDS = frozenset(
    {
        "the",
        "a",
        "an",
        "is",
        "are",
        "was",
        "were",
        "be",
        "been",
        "being",
        "have",
        "has",
        "had",
        "do",
        "does",
        "did",
        "will",
        "would",
        "could",
        "should",
        "may",
        "might",
        "shall",
        "can",
        "it",
        "its",
        "this",
        "that",
        "these",
        "those",
        "i",
        "you",
        "he",
        "she",
        "we",
        "they",
        "me",
        "him",
        "her",
        "us",
        "them",
        "my",
        "your",
        "his",
        "our",
        "their",
        "in",
        "on",
        "at",
        "to",
        "for",
        "of",
        "with",
        "by",
        "from",
        "and",
        "or",
        "but",
        "not",
    }
)


def _tokenize(text: str) -> list[str]:
    """Tokenize text for BM25: lowercase, extract words, remove stop words."""
    tokens = re.findall(r"[a-z0-9]+", text.lower())
    return [t for t in tokens if t not in _STOP_WORDS]


@dataclass
class RetrievedChunk:
    content: str
    source: str
    section: str
    score: float


class Retriever:
    def __init__(self, vector_store: VectorStore, embedding_client: EmbeddingClient, config: RetrievalConfig) -> None:
        self.vector_store = vector_store
        self.embedding_client = embedding_client
        self.config = config
        self._bm25: BM25Okapi | None = None
        self._bm25_chunks: list[dict[str, Any]] | None = None
        self._bm25_corpus: list[list[str]] | None = None
        self._bm25_count: int = 0
        self._bm25_lock = threading.Lock()

    def retrieve(self, query: str) -> list[RetrievedChunk]:
        query_embedding = self.embedding_client.embed_query(query)

        if self.config.method == "bm25":
            return self._retrieve_bm25(query)

        n_candidates = self.config.top_k * 2
        vector_results = self.vector_store.query(query_embedding, n=n_candidates)

        if self.config.method == "vector":
            return [
                RetrievedChunk(content=r["content"], source=r["source"], section=r.get("section", ""), score=s)
                for r, s in vector_results
                if s >= self.config.min_score
            ][: self.config.top_k]

        # Hybrid: vector → BM25 re-rank
        if vector_results:
            filtered = [(r, s) for r, s in vector_results if s >= self.config.min_score]
            if filtered:
                return self._hybrid_rerank(query, filtered)

        return [
            RetrievedChunk(content=r["content"], source=r["source"], section=r.get("section", ""), score=s)
            for r, s in vector_results[: self.config.top_k]
        ]

    def _retrieve_bm25(self, query: str) -> list[RetrievedChunk]:
        bm25, chunks = self._get_bm25_index()
        if not chunks:
            return []
        tokenized_query = _tokenize(query)
        scores = bm25.get_scores(tokenized_query)
        ranked = sorted(enumerate(scores), key=lambda x: x[1], reverse=True)
        return [
            RetrievedChunk(
                content=chunks[i]["content"],
                source=chunks[i]["source"],
                section=chunks[i].get("section", ""),
                score=float(s),
            )
            for i, s in ranked[: self.config.top_k]
        ]

    def _get_bm25_index(self) -> tuple[BM25Okapi, list[dict[str, Any]]]:
        current_count = self.vector_store.count()
        with self._bm25_lock:
            if self._bm25 is not None and self._bm25_count == current_count:
                assert self._bm25_chunks is not None
                return self._bm25, self._bm25_chunks
            raw_chunks = self.vector_store.get_all_chunks()
            self._bm25_chunks = [
                {"content": c["content"], "source": c["source"], "section": c.get("section", "")} for c in raw_chunks
            ]
            self._bm25_corpus = [_tokenize(c["content"]) for c in raw_chunks]
            self._bm25 = BM25Okapi(self._bm25_corpus)
            self._bm25_count = current_count
            logger.debug("Built BM25 index with %d chunks", current_count)
            return self._bm25, self._bm25_chunks

    def _hybrid_rerank(self, query: str, candidates: list[tuple[QueryResult, float]]) -> list[RetrievedChunk]:
        if not candidates:
            return []
        tokenized_corpus = [_tokenize(c[0]["content"]) for c in candidates]
        bm25 = BM25Okapi(tokenized_corpus)
        tokenized_query = _tokenize(query)
        bm25_scores = bm25.get_scores(tokenized_query)

        max_bm25 = max(bm25_scores) if len(bm25_scores) > 0 and max(bm25_scores) > 0 else 1.0
        combined: list[tuple[QueryResult, float]] = []
        for i, (chunk, vec_score) in enumerate(candidates):
            bm25_norm = bm25_scores[i] / max_bm25
            combined_score = VECTOR_WEIGHT * vec_score + BM25_WEIGHT * bm25_norm
            combined.append((chunk, combined_score))

        combined.sort(key=lambda x: x[1], reverse=True)
        return [
            RetrievedChunk(content=r["content"], source=r["source"], section=r.get("section", ""), score=s)
            for r, s in combined[: self.config.top_k]
        ]

    def format_context(self, chunks: list[RetrievedChunk]) -> str:
        parts: list[str] = []
        for chunk in chunks:
            if chunk.section:
                header = f"[Source: {chunk.source}, Section: {chunk.section}]"
            else:
                header = f"[Source: {chunk.source}]"
            parts.append(f"{header}\n{chunk.content}")
        return "\n\n".join(parts)
