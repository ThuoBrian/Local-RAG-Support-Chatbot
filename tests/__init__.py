"""Shared test fixtures for helpdesk-rag."""

import pytest

from helpdesk_rag.config import RAGConfig


@pytest.fixture
def default_config() -> RAGConfig:
    return RAGConfig()


@pytest.fixture
def chunker(default_config: RAGConfig):
    from helpdesk_rag.chunker import RecursiveChunker
    return RecursiveChunker(default_config.chunking)