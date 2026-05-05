from __future__ import annotations

import logging

from openai import OpenAI

from helpdesk_rag.config import OllamaConfig
from helpdesk_rag.exceptions import EmbeddingError

logger = logging.getLogger(__name__)


def create_openai_client(config: OllamaConfig, timeout: float = 60.0) -> OpenAI:
    """Create a shared OpenAI client with proper timeout and retry."""
    return OpenAI(
        base_url=config.base_url,
        api_key="ollama",
        timeout=timeout,
        max_retries=2,
    )


class EmbeddingClient:
    def __init__(self, config: OllamaConfig) -> None:
        self.model = config.embedding_model
        self.client = create_openai_client(config)

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        try:
            response = self.client.embeddings.create(model=self.model, input=texts)
        except Exception as exc:
            raise EmbeddingError(f"Embedding API call failed: {exc}") from exc
        logger.debug("Embedded %d texts", len(texts))
        return [d.embedding for d in response.data]

    def embed_query(self, text: str) -> list[float]:
        try:
            response = self.client.embeddings.create(model=self.model, input=text)
        except Exception as exc:
            raise EmbeddingError(f"Embedding query failed: {exc}") from exc
        return response.data[0].embedding
