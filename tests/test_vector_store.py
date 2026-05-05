"""Tests for helpdesk_rag.vector_store."""

from unittest.mock import MagicMock, patch

import pytest

from helpdesk_rag.config import VectorStoreConfig
from helpdesk_rag.exceptions import VectorStoreError


class TestVectorStoreInit:
    @patch("helpdesk_rag.vector_store.chromadb")
    def test_init_success(self, mock_chromadb):
        mock_client = MagicMock()
        mock_collection = MagicMock()
        mock_collection.count.return_value = 0
        mock_collection.get.return_value = {"metadatas": []}
        mock_chromadb.PersistentClient.return_value = mock_client
        mock_client.get_or_create_collection.return_value = mock_collection

        from helpdesk_rag.vector_store import VectorStore
        vs = VectorStore(VectorStoreConfig())
        assert vs.collection is mock_collection

    @patch("helpdesk_rag.vector_store.chromadb")
    def test_init_failure_raises(self, mock_chromadb):
        mock_chromadb.PersistentClient.side_effect = Exception("db error")

        from helpdesk_rag.vector_store import VectorStore
        with pytest.raises(VectorStoreError, match="Failed to initialize"):
            VectorStore(VectorStoreConfig())


class TestVectorStoreQuery:
    @patch("helpdesk_rag.vector_store.chromadb")
    def test_query_returns_results(self, mock_chromadb):
        mock_client = MagicMock()
        mock_collection = MagicMock()
        mock_collection.count.return_value = 2
        mock_collection.get.return_value = {"metadatas": [{"source": "doc1"}, {"source": "doc2"}]}
        mock_collection.query.return_value = {
            "ids": [["id1", "id2"]],
            "documents": [["content one", "content two"]],
            "metadatas": [[{"source": "doc1.md", "section": "Intro"}, {"source": "doc2.md", "section": ""}]],
            "distances": [[0.4, 0.8]],
        }
        mock_chromadb.PersistentClient.return_value = mock_client
        mock_client.get_or_create_collection.return_value = mock_collection

        from helpdesk_rag.vector_store import VectorStore
        vs = VectorStore(VectorStoreConfig())
        results = vs.query([0.1] * 384, n=2)
        assert len(results) == 2
        assert results[0][1] >= 0
        assert results[0][0]["source"] == "doc1.md"

    @patch("helpdesk_rag.vector_store.chromadb")
    def test_query_empty_results(self, mock_chromadb):
        mock_client = MagicMock()
        mock_collection = MagicMock()
        mock_collection.count.return_value = 0
        mock_collection.get.return_value = {"metadatas": []}
        mock_collection.query.return_value = {"ids": [[]]}
        mock_chromadb.PersistentClient.return_value = mock_client
        mock_client.get_or_create_collection.return_value = mock_collection

        from helpdesk_rag.vector_store import VectorStore
        vs = VectorStore(VectorStoreConfig())
        results = vs.query([0.1] * 384)
        assert results == []

    @patch("helpdesk_rag.vector_store.chromadb")
    def test_add_chunks_mismatched_lengths_raises(self, mock_chromadb):
        mock_client = MagicMock()
        mock_collection = MagicMock()
        mock_collection.count.return_value = 0
        mock_collection.get.return_value = {"metadatas": []}
        mock_chromadb.PersistentClient.return_value = mock_client
        mock_client.get_or_create_collection.return_value = mock_collection

        from helpdesk_rag.chunker import Chunk
        from helpdesk_rag.vector_store import VectorStore

        vs = VectorStore(VectorStoreConfig())
        chunks = [Chunk(id="c1", content="text", metadata={"source": "doc.md", "format": "text"})]
        with pytest.raises(VectorStoreError, match="must have the same length"):
            vs.add_chunks(chunks, [[0.1], [0.2]])

    @patch("helpdesk_rag.vector_store.chromadb")
    def test_score_conversion(self, mock_chromadb):
        mock_client = MagicMock()
        mock_collection = MagicMock()
        mock_collection.count.return_value = 1
        mock_collection.get.return_value = {"metadatas": [{"source": "doc1"}]}
        mock_collection.query.return_value = {
            "ids": [["id1"]],
            "documents": [["content"]],
            "metadatas": [[{"source": "doc.md", "section": ""}]],
            "distances": [[0.4]],
        }
        mock_chromadb.PersistentClient.return_value = mock_client
        mock_client.get_or_create_collection.return_value = mock_collection

        from helpdesk_rag.vector_store import VectorStore
        vs = VectorStore(VectorStoreConfig())
        results = vs.query([0.1] * 384, n=1)
        assert len(results) == 1
        assert abs(results[0][1] - 0.8) < 0.001


class TestVectorStoreGetSources:
    @patch("helpdesk_rag.vector_store.chromadb")
    def test_get_sources_sorted(self, mock_chromadb):
        mock_client = MagicMock()
        mock_collection = MagicMock()
        mock_collection.count.return_value = 2
        mock_collection.get.return_value = {
            "metadatas": [{"source": "b.md"}, {"source": "a.md"}],
        }
        mock_chromadb.PersistentClient.return_value = mock_client
        mock_client.get_or_create_collection.return_value = mock_collection

        from helpdesk_rag.vector_store import VectorStore
        vs = VectorStore(VectorStoreConfig())
        sources = vs.get_sources()
        assert sources == ["a.md", "b.md"]

    @patch("helpdesk_rag.vector_store.chromadb")
    def test_get_sources_empty(self, mock_chromadb):
        mock_client = MagicMock()
        mock_collection = MagicMock()
        mock_collection.count.return_value = 0
        mock_collection.get.return_value = {"metadatas": []}
        mock_chromadb.PersistentClient.return_value = mock_client
        mock_client.get_or_create_collection.return_value = mock_collection

        from helpdesk_rag.vector_store import VectorStore
        vs = VectorStore(VectorStoreConfig())
        sources = vs.get_sources()
        assert sources == []