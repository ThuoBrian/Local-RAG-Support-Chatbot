from __future__ import annotations

import logging
from typing import TypedDict

import chromadb
from chromadb.config import Settings

from helpdesk_rag.chunker import Chunk
from helpdesk_rag.config import VectorStoreConfig
from helpdesk_rag.exceptions import VectorStoreError

logger = logging.getLogger(__name__)


class QueryResult(TypedDict, total=False):
    id: str
    content: str
    source: str
    format: str
    section: str


class ChunkResult(TypedDict, total=False):
    id: str
    content: str
    source: str
    section: str


class VectorStore:
    def __init__(self, config: VectorStoreConfig) -> None:
        try:
            self.client = chromadb.PersistentClient(
                path=config.persist_dir,
                settings=Settings(anonymized_telemetry=False),
            )
            self.collection = self.client.get_or_create_collection(
                name=config.collection_name,
                metadata={"hnsw:space": "cosine"},
            )
        except Exception as exc:
            raise VectorStoreError(f"Failed to initialize vector store: {exc}") from exc
        logger.info("Vector store initialized: %d chunks in %s sources", self.collection.count(), len(self.get_sources()))

    def add_chunks(self, chunks: list[Chunk], embeddings: list[list[float]]) -> None:
        if len(chunks) != len(embeddings):
            raise VectorStoreError(f"chunks ({len(chunks)}) and embeddings ({len(embeddings)}) must have the same length")
        if not chunks:
            return

        ids = [c.id for c in chunks]
        documents = [c.content for c in chunks]
        metadatas = []
        for c in chunks:
            headings = c.metadata.get("headings", [])
            metadatas.append({
                "source": c.metadata.get("source", ""),
                "format": c.metadata.get("format", ""),
                "chunk_index": c.metadata.get("chunk_index", 0),
                "section": headings[-1] if headings else "",
            })

        existing = set(self.collection.get()["ids"])
        new_items = [(id_, doc, emb, meta) for id_, doc, emb, meta in zip(ids, documents, embeddings, metadatas) if id_ not in existing]
        skipped = len(chunks) - len(new_items)
        if skipped:
            logger.warning("Skipped %d existing chunk(s) during ingestion", skipped)

        if not new_items:
            return

        nids, ndocs, nembs, nmetas = zip(*new_items)
        try:
            self.collection.add(ids=list(nids), documents=list(ndocs), embeddings=list(nembs), metadatas=list(nmetas))
        except Exception as exc:
            raise VectorStoreError(f"Failed to add chunks: {exc}") from exc
        logger.info("Added %d chunks to vector store", len(new_items))

    def query(self, query_embedding: list[float], n: int = 8) -> list[tuple[QueryResult, float]]:
        try:
            results = self.collection.query(query_embeddings=[query_embedding], n_results=n)
        except Exception as exc:
            raise VectorStoreError(f"Vector store query failed: {exc}") from exc
        items: list[tuple[QueryResult, float]] = []
        if not results["ids"] or not results["ids"][0]:
            return items
        for i in range(len(results["ids"][0])):
            metadata = results["metadatas"][0][i] if results["metadatas"] else {}
            distance = results["distances"][0][i] if results["distances"] else 0.0
            score = max(0.0, 1.0 - (distance / 2.0))
            items.append(({
                "id": results["ids"][0][i],
                "content": results["documents"][0][i] if results["documents"] else "",
                "source": metadata.get("source", ""),
                "format": metadata.get("format", ""),
                "section": metadata.get("section", ""),
            }, score))
        return items

    def get_sources(self) -> list[str]:
        result = self.collection.get(include=["metadatas"])
        metadatas = result["metadatas"]
        sources: set[str] = set()
        for m in metadatas:
            if m and m.get("source"):
                sources.add(m["source"])
        return sorted(sources)

    def count(self) -> int:
        return self.collection.count()

    def get_all_documents(self) -> list[str]:
        return self.collection.get()["documents"] or []

    def get_all_chunks(self) -> list[ChunkResult]:
        result = self.collection.get()
        if not result["ids"]:
            return []
        chunks: list[ChunkResult] = []
        for i in range(len(result["ids"])):
            metadata = result["metadatas"][i] if result["metadatas"] else {}
            chunks.append({
                "id": result["ids"][i],
                "content": result["documents"][i] if result["documents"] else "",
                "source": metadata.get("source", ""),
                "section": metadata.get("section", ""),
            })
        return chunks