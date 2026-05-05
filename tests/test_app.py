"""Tests for helpdesk_rag.app."""

import json
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from helpdesk_rag.app import (
    MAX_SESSIONS,
    SESSION_MAX_AGE,
    CSPMiddleware,
    ChatRequest,
    app,
)


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def mock_engine():
    with patch("helpdesk_rag.app._engine") as mock:
        yield mock


class TestChatRequest:
    def test_valid_request(self):
        req = ChatRequest(message="hello", session_id="abc-123")
        assert req.message == "hello"
        assert req.session_id == "abc-123"

    def test_empty_message_rejected(self):
        with pytest.raises(Exception):
            ChatRequest(message="", session_id="abc-123")

    def test_long_message_rejected(self):
        with pytest.raises(Exception):
            ChatRequest(message="x" * 10001, session_id="abc-123")

    def test_invalid_session_id_rejected(self):
        with pytest.raises(Exception):
            ChatRequest(message="hello", session_id="invalid session!")

    def test_session_id_with_special_chars_rejected(self):
        with pytest.raises(Exception):
            ChatRequest(message="hello", session_id="abc 123")


class TestCSPMiddleware:
    def test_csp_header_set(self, client):
        response = client.get("/")
        assert "content-security-policy" in response.headers
        csp = response.headers["content-security-policy"]
        assert "default-src 'self'" in csp
        assert "script-src 'self' cdn.jsdelivr.net" in csp


class TestSessionValidation:
    def test_valid_session_id_format(self):
        req = ChatRequest(message="test", session_id="a1b2c3d4-e5f6-7890-abcd-ef1234567890")
        assert req.session_id == "a1b2c3d4-e5f6-7890-abcd-ef1234567890"

    def test_short_session_id(self):
        req = ChatRequest(message="test", session_id="abc")
        assert req.session_id == "abc"