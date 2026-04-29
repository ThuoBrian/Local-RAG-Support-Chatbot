from __future__ import annotations

import logging
from collections.abc import Generator

from helpdesk_rag.config import OllamaConfig
from helpdesk_rag.embeddings import create_openai_client
from helpdesk_rag.exceptions import LLMError

logger = logging.getLogger(__name__)


class LLMClient:
    def __init__(self, config: OllamaConfig) -> None:
        self.model = config.llm_model
        self.temperature = config.temperature
        self.max_tokens = config.max_tokens
        self.client = create_openai_client(config)

    def generate(self, system_prompt: str, user_message: str) -> str:
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ]
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
            )
        except Exception as exc:
            raise LLMError(f"LLM generation failed: {exc}") from exc
        content = response.choices[0].message.content
        logger.debug("LLM generated %d chars", len(content) if content else 0)
        return content if content else ""

    def generate_stream(self, system_prompt: str, user_message: str) -> Generator[str, None, None]:
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ]
        try:
            stream = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                stream=True,
            )
        except Exception as exc:
            raise LLMError(f"LLM stream failed: {exc}") from exc
        for chunk in stream:
            delta = chunk.choices[0].delta
            if delta.content:
                yield delta.content