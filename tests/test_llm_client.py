"""Tests for helpdesk_rag.llm_client."""

from unittest.mock import MagicMock, patch

import pytest

from helpdesk_rag.config import OllamaConfig
from helpdesk_rag.exceptions import LLMError


class TestLLMClientGenerate:
    @patch("helpdesk_rag.llm_client.create_openai_client")
    def test_generate_returns_content(self, mock_create):
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Hello from the model"
        mock_client.chat.completions.create.return_value = mock_response
        mock_create.return_value = mock_client

        from helpdesk_rag.llm_client import LLMClient
        client = LLMClient(OllamaConfig())
        result = client.generate("You are helpful.", "Say hello")
        assert result == "Hello from the model"
        mock_client.chat.completions.create.assert_called_once()

    @patch("helpdesk_rag.llm_client.create_openai_client")
    def test_generate_empty_content(self, mock_create):
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = None
        mock_client.chat.completions.create.return_value = mock_response
        mock_create.return_value = mock_client

        from helpdesk_rag.llm_client import LLMClient
        client = LLMClient(OllamaConfig())
        result = client.generate("sys", "msg")
        assert result == ""

    @patch("helpdesk_rag.llm_client.create_openai_client")
    def test_generate_raises_llm_error(self, mock_create):
        mock_client = MagicMock()
        mock_client.chat.completions.create.side_effect = Exception("connection failed")
        mock_create.return_value = mock_client

        from helpdesk_rag.llm_client import LLMClient
        client = LLMClient(OllamaConfig())
        with pytest.raises(LLMError, match="LLM generation failed"):
            client.generate("sys", "msg")


class TestLLMClientGenerateStream:
    @patch("helpdesk_rag.llm_client.create_openai_client")
    def test_generate_stream_yields_tokens(self, mock_create):
        mock_client = MagicMock()
        chunks = []
        for text in ["Hello", " world"]:
            chunk = MagicMock()
            chunk.choices = [MagicMock()]
            chunk.choices[0].delta.content = text
            chunks.append(chunk)

        # End marker with no content
        end_chunk = MagicMock()
        end_chunk.choices = [MagicMock()]
        end_chunk.choices[0].delta.content = None
        chunks.append(end_chunk)

        mock_client.chat.completions.create.return_value = iter(chunks)
        mock_create.return_value = mock_client

        from helpdesk_rag.llm_client import LLMClient
        client = LLMClient(OllamaConfig())
        tokens = list(client.generate_stream("sys", "msg"))
        assert "Hello" in tokens
        assert " world" in tokens

    @patch("helpdesk_rag.llm_client.create_openai_client")
    def test_generate_stream_raises_llm_error_on_create_failure(self, mock_create):
        mock_client = MagicMock()
        mock_client.chat.completions.create.side_effect = Exception("stream create failed")
        mock_create.return_value = mock_client

        from helpdesk_rag.llm_client import LLMClient
        client = LLMClient(OllamaConfig())
        with pytest.raises(LLMError, match="LLM stream failed"):
            list(client.generate_stream("sys", "msg"))

    @patch("helpdesk_rag.llm_client.create_openai_client")
    def test_generate_stream_raises_llm_error_on_iter_failure(self, mock_create):
        mock_client = MagicMock()

        def broken_iter(*args, **kwargs):
            yield MagicMock()  # First chunk works
            raise Exception("stream interrupted")

        mock_client.chat.completions.create.return_value = broken_iter()
        mock_create.return_value = mock_client

        from helpdesk_rag.llm_client import LLMClient
        client = LLMClient(OllamaConfig())
        with pytest.raises(LLMError, match="LLM stream interrupted"):
            list(client.generate_stream("sys", "msg"))