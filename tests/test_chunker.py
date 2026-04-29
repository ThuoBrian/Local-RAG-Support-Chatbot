"""Tests for helpdesk_rag.chunker."""

from helpdesk_rag.chunker import RecursiveChunker, _split_text
from helpdesk_rag.config import ChunkingConfig
from helpdesk_rag.loader import Document


class TestRecursiveChunker:
    def test_basic_chunking(self):
        config = ChunkingConfig(chunk_size=100, chunk_overlap=20)
        chunker = RecursiveChunker(config)
        doc = Document(content="Word " * 200, metadata={"source": "test.txt", "format": "text"})
        chunks = chunker.chunk(doc)
        assert len(chunks) > 1
        assert all(c.metadata["source"] == "test.txt" for c in chunks)

    def test_empty_string(self):
        config = ChunkingConfig(chunk_size=100, chunk_overlap=20)
        chunker = RecursiveChunker(config)
        doc = Document(content="", metadata={"source": "empty.txt", "format": "text"})
        chunks = chunker.chunk(doc)
        assert chunks == []

    def test_oversized_segment(self):
        config = ChunkingConfig(chunk_size=50, chunk_overlap=10)
        chunker = RecursiveChunker(config)
        doc = Document(content="A" * 200, metadata={"source": "big.txt", "format": "text"})
        chunks = chunker.chunk(doc)
        assert len(chunks) > 1

    def test_content_preservation(self):
        config = ChunkingConfig(chunk_size=200, chunk_overlap=50)
        chunker = RecursiveChunker(config)
        text = "Hello world. " * 50
        doc = Document(content=text, metadata={"source": "test.txt", "format": "text"})
        chunks = chunker.chunk(doc)
        # All original words should appear in chunks
        for word in ["Hello", "world"]:
            assert any(word in c.content for c in chunks)


class TestSplitText:
    def test_overlap_less_than_size(self):
        with __import__("pytest").raises(ValueError):
            ChunkingConfig(chunk_size=50, chunk_overlap=50)

    def test_split_respects_separators(self):
        text = "## Section 1\nParagraph one.\n\n## Section 2\nParagraph two."
        chunks = _split_text(text, chunk_size=500, chunk_overlap=50)
        # Should produce at least one chunk
        assert len(chunks) >= 1
        assert "Section 1" in chunks[0]