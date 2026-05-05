"""Tests for helpdesk_rag.embeddings."""

from unittest.mock import MagicMock, patch

import pytest

from helpdesk_rag.config import OllamaConfig
from helpdesk_rag.exceptions import EmbeddingError


class TestEmbeddingClient:
    @patch("helpdesk_rag.embeddings.create_openai_client")
    def test_embed_texts(self, mock_create):
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.data = [MagicMock(embedding=[0.1, 0.2]), MagicMock(embedding=[0.3, 0.4])]
        mock_client.embeddings.create.return_value = mock_response
        mock_create.return_value = mock_client

        from helpdesk_rag.embeddings import EmbeddingClient
        client = EmbeddingClient(OllamaConfig())
        result = client.embed_texts(["hello", "world"])
        assert len(result) == 2
        assert result[0] == [0.1, 0.2]
        assert result[1] == [0.3, 0.4]

    @patch("helpdesk_rag.embeddings.create_openai_client")
    def test_embed_texts_empty(self, mock_create):
        mock_client = MagicMock()
        mock_create.return_value = mock_client

        from helpdesk_rag.embeddings import EmbeddingClient
        client = EmbeddingClient(OllamaConfig())
        result = client.embed_texts([])
        assert result == []
        mock_client.embeddings.create.assert_not_called()

    @patch("helpdesk_rag.embeddings.create_openai_client")
    def test_embed_query(self, mock_create):
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.data = [MagicMock(embedding=[0.5, 0.6])]
        mock_client.embeddings.create.return_value = mock_response
        mock_create.return_value = mock_client

        from helpdesk_rag.embeddings import EmbeddingClient
        client = EmbeddingClient(OllamaConfig())
        result = client.embed_query("test query")
        assert result == [0.5, 0.6]

    @patch("helpdesk_rag.embeddings.create_openai_client")
    def test_embed_texts_error(self, mock_create):
        mock_client = MagicMock()
        mock_client.embeddings.create.side_effect = Exception("API error")
        mock_create.return_value = mock_client

        from helpdesk_rag.embeddings import EmbeddingClient
        client = EmbeddingClient(OllamaConfig())
        with pytest.raises(EmbeddingError, match="Embedding API call failed"):
            client.embed_texts(["test"])

    @patch("helpdesk_rag.embeddings.create_openai_client")
    def test_embed_query_error(self, mock_create):
        mock_client = MagicMock()
        mock_client.embeddings.create.side_effect = Exception("API error")
        mock_create.return_value = mock_client

        from helpdesk_rag.embeddings import EmbeddingClient
        client = EmbeddingClient(OllamaConfig())
        with pytest.raises(EmbeddingError, match="Embedding query failed"):
            client.embed_query("test")


class TestCreateOpenAIClient:
    def test_creates_client_with_config(self):
        config = OllamaConfig()
        from helpdesk_rag.embeddings import create_openai_client
        client = create_openai_client(config)
        assert client is not None