"""Custom exception hierarchy for helpdesk-rag."""


class HelpdeskRAGError(Exception):
    """Base exception for all helpdesk-rag errors."""


class ConfigError(HelpdeskRAGError):
    """Configuration loading or validation error."""


class DocumentLoadError(HelpdeskRAGError):
    """Error loading or parsing a document."""


class EmbeddingError(HelpdeskRAGError):
    """Error generating embeddings."""


class LLMError(HelpdeskRAGError):
    """Error calling the LLM."""


class VectorStoreError(HelpdeskRAGError):
    """Error interacting with the vector store."""


class RetrievalError(HelpdeskRAGError):
    """Error during retrieval."""
