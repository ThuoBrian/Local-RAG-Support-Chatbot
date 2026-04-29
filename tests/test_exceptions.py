"""Tests for helpdesk_rag.exceptions."""

from helpdesk_rag.exceptions import (
    ConfigError,
    DocumentLoadError,
    EmbeddingError,
    HelpdeskRAGError,
    LLMError,
    RetrievalError,
    VectorStoreError,
)


def test_hierarchy():
    for exc_cls in [ConfigError, DocumentLoadError, EmbeddingError, LLMError, VectorStoreError, RetrievalError]:
        assert issubclass(exc_cls, HelpdeskRAGError)
        inst = exc_cls("test")
        assert isinstance(inst, HelpdeskRAGError)
        assert isinstance(inst, Exception)