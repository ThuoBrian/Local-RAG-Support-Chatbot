from __future__ import annotations

import logging
from dataclasses import dataclass, field

from typing import cast

from helpdesk_rag.config import ChunkingConfig
from helpdesk_rag.loader import Document, DocumentMetadata

logger = logging.getLogger(__name__)

TRAILING_CHUNK_MERGE_THRESHOLD = 0.3

SEPARATORS = ["\n## ", "\n# ", "\n\n", "\n", ". ", "? ", "! ", "; ", ", ", " "]


class ChunkMetadata(DocumentMetadata, total=False):
    chunk_index: int


@dataclass
class Chunk:
    id: str
    content: str
    metadata: ChunkMetadata = field(default_factory=cast(type, dict))


class RecursiveChunker:
    def __init__(self, config: ChunkingConfig) -> None:
        self.chunk_size = config.chunk_size
        self.chunk_overlap = config.chunk_overlap

    def chunk(self, doc: Document) -> list[Chunk]:
        chunks = _split_text(doc.content, self.chunk_size, self.chunk_overlap)
        result = [
            Chunk(
                id=f"{doc.metadata['source']}::{i}",
                content=chunk,
                metadata={**doc.metadata, "chunk_index": i},
            )
            for i, chunk in enumerate(chunks)
        ]
        logger.debug("Chunked %s into %d chunks", doc.metadata.get("source", "?"), len(result))
        return result


def _split_text(text: str, chunk_size: int, chunk_overlap: int) -> list[str]:
    chunks: list[str] = []
    current = ""

    for segment in _split_on_separators(text):
        if not segment:
            continue
        segment_len = len(segment)

        if segment_len > chunk_size:
            if current:
                chunks.append(current.strip())
                current = ""
            for i in range(0, segment_len, chunk_size - chunk_overlap):
                sub = segment[i : i + chunk_size]
                if sub.strip():
                    chunks.append(sub.strip())
        elif len(current) + len(segment) > chunk_size:
            chunks.append(current.strip())
            current = segment
        else:
            current += segment

    if current.strip():
        chunks.append(current.strip())

    if len(chunks) > 1 and len(chunks[-1]) < chunk_size * TRAILING_CHUNK_MERGE_THRESHOLD:
        if len(chunks[-2]) + len(chunks[-1]) <= chunk_size:
            chunks[-2] += chunks[-1]
            chunks.pop()

    return chunks


def _split_on_separators(text: str) -> list[str]:
    segments = [text]
    for sep in SEPARATORS:
        if not sep:
            continue
        new_segments: list[str] = []
        for seg in segments:
            parts = seg.split(sep)
            for i, part in enumerate(parts):
                if i == 0:
                    new_segments.append(part)
                else:
                    new_segments.append(sep + part)
        segments = new_segments
    return [s for s in segments if s.strip()]
