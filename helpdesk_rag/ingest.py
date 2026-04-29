"""Ingestion script: loads documents from data/documents/, chunks, embeds, and stores in ChromaDB."""

from __future__ import annotations

import logging
import sys
from pathlib import Path

from tqdm import tqdm

from helpdesk_rag.chunker import RecursiveChunker
from helpdesk_rag.config import load_config
from helpdesk_rag.embeddings import EmbeddingClient
from helpdesk_rag.loader import SUPPORTED_EXTENSIONS, load_document
from helpdesk_rag.logging_config import setup_logging
from helpdesk_rag.vector_store import VectorStore

logger = logging.getLogger(__name__)


def ingest(docs_dir: str = "data/documents") -> int:
    setup_logging()
    config = load_config()

    chunker = RecursiveChunker(config.chunking)
    embedding_client = EmbeddingClient(config.ollama)
    vector_store = VectorStore(config.vector_store)

    docs_path = Path(docs_dir)
    if not docs_path.exists():
        logger.error("Directory not found: %s", docs_dir)
        return 1

    files = sorted(
        f for f in docs_path.iterdir()
        if f.is_file() and f.suffix.lower() in SUPPORTED_EXTENSIONS
    )

    if not files:
        logger.warning("No supported documents found in %s/", docs_dir)
        logger.info("Supported formats: %s", sorted(SUPPORTED_EXTENSIONS))
        return 0

    total_chunks = 0
    file_bar = tqdm(files, desc="Processing documents", unit="file")

    for file_path in file_bar:
        file_bar.set_postfix(file=file_path.name, refresh=False)
        try:
            doc = load_document(file_path)
        except Exception:
            logger.exception("Failed to load %s, skipping", file_path.name)
            continue
        chunks = chunker.chunk(doc)
        tqdm.write(f"  {file_path.name} -> {len(chunks)} chunks")

        texts = [c.content for c in chunks]
        embed_bar = tqdm(
            [texts],
            desc="  Embedding",
            unit="batch",
            leave=False,
        )
        for batch_texts in embed_bar:
            embeddings = embedding_client.embed_texts(batch_texts)
        embed_bar.close()

        vector_store.add_chunks(chunks, embeddings)
        total_chunks += len(chunks)

    file_bar.close()

    source_count = len(vector_store.get_sources())
    store_count = vector_store.count()
    print(f"\nDone. {len(files)} documents -> {total_chunks} chunks indexed.")
    print(f"Vector store: {store_count} total chunks across {source_count} sources.")
    return 0


def main() -> None:
    docs_dir = sys.argv[1] if len(sys.argv) > 1 else "data/documents"
    sys.exit(ingest(docs_dir))


if __name__ == "__main__":
    main()