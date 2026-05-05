"""Tests for helpdesk_rag.retriever."""

from unittest.mock import MagicMock, patch

import pytest

from helpdesk_rag.config import RetrievalConfig
from helpdesk_rag.retriever import RetrievedChunk, Retriever, _tokenize


class TestTokenize:
    def test_basic_tokenization(self):
        tokens = _tokenize("Hello World Test")
        assert "hello" in tokens
        assert "world" in tokens
        assert "test" in tokens

    def test_removes_stop_words(self):
        tokens = _tokenize("the quick brown fox is a test")
        assert "the" not in tokens
        assert "is" not in tokens
        assert "a" not in tokens
        assert "quick" in tokens

    def test_lowercase(self):
        tokens = _tokenize("UPPERCASE Words")
        assert all(t == t.lower() for t in tokens)

    def test_extracts_numbers(self):
        tokens = _tokenize("version 2.0 step 3")
        assert "2" in tokens
        assert "3" in tokens

    def test_empty_string(self):
        assert _tokenize("") == []


class TestRetriever:
    @pytest.fixture
    def mock_store(self):
        store = MagicMock()
        store.count.return_value = 2
        store.get_all_chunks.return_value = [
            {"content": "encryption is important", "source": "doc1.md", "section": "Security"},
            {"content": "backup your files regularly", "source": "doc2.md", "section": "Backup"},
        ]
        return store

    @pytest.fixture
    def mock_embedding_client(self):
        client = MagicMock()
        client.embed_query.return_value = [0.1] * 384
        return client

    def test_vector_retrieval(self, mock_store, mock_embedding_client):
        config = RetrievalConfig(method="vector", top_k=2, min_score=0.1)
        mock_store.query.return_value = [
            ({"content": "encryption is important", "source": "doc1.md", "section": "Security"}, 0.8),
            ({"content": "backup your files regularly", "source": "doc2.md", "section": "Backup"}, 0.6),
        ]
        retriever = Retriever(mock_store, mock_embedding_client, config)
        results = retriever.retrieve("how to encrypt")
        assert len(results) == 2
        assert results[0].source == "doc1.md"
        assert results[0].score == 0.8

    def test_vector_retrieval_filters_low_scores(self, mock_store, mock_embedding_client):
        config = RetrievalConfig(method="vector", top_k=5, min_score=0.5)
        mock_store.query.return_value = [
            ({"content": "good result", "source": "doc1.md", "section": ""}, 0.8),
            ({"content": "bad result", "source": "doc2.md", "section": ""}, 0.1),
        ]
        retriever = Retriever(mock_store, mock_embedding_client, config)
        results = retriever.retrieve("test")
        assert len(results) == 1
        assert results[0].score == 0.8

    def test_hybrid_retrieval_with_empty_candidates(self, mock_store, mock_embedding_client):
        config = RetrievalConfig(method="hybrid", top_k=2, min_score=0.9)
        mock_store.query.return_value = [
            ({"content": "low score", "source": "doc1.md", "section": ""}, 0.1),
        ]
        retriever = Retriever(mock_store, mock_embedding_client, config)
        # Should not crash — empty filtered list is handled
        results = retriever.retrieve("test")
        assert isinstance(results, list)

    def test_bm25_retrieval(self, mock_store, mock_embedding_client):
        config = RetrievalConfig(method="bm25", top_k=2)
        retriever = Retriever(mock_store, mock_embedding_client, config)
        results = retriever.retrieve("encryption")
        assert len(results) <= 2

    def test_format_context(self, mock_store, mock_embedding_client):
        config = RetrievalConfig()
        retriever = Retriever(mock_store, mock_embedding_client, config)
        chunks = [
            RetrievedChunk(content="content one", source="doc1.md", section="Intro", score=0.9),
            RetrievedChunk(content="content two", source="doc2.md", section="", score=0.7),
        ]
        context = retriever.format_context(chunks)
        assert "[Source: doc1.md, Section: Intro]" in context
        assert "content one" in context
        assert "[Source: doc2.md]" in context

    def test_retrieved_chunk_dataclass(self):
        chunk = RetrievedChunk(content="test", source="doc.md", section="Sec", score=0.95)
        assert chunk.content == "test"
        assert chunk.source == "doc.md"
        assert chunk.section == "Sec"
        assert chunk.score == 0.95