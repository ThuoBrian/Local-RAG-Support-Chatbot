from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Literal

import yaml
from pydantic import BaseModel, field_validator, model_validator

logger = logging.getLogger(__name__)


class OllamaConfig(BaseModel):
    base_url: str = "http://localhost:11434/v1"
    embedding_model: str = "nomic-embed-text"
    llm_model: str = "glm-5.1:cloud"
    temperature: float = 0.3
    max_tokens: int = 768

    @field_validator("temperature")
    @classmethod
    def temperature_range(cls, v: float) -> float:
        if not 0.0 <= v <= 2.0:
            raise ValueError("temperature must be between 0.0 and 2.0")
        return v

    @field_validator("max_tokens")
    @classmethod
    def max_tokens_positive(cls, v: int) -> int:
        if v < 1:
            raise ValueError("max_tokens must be at least 1")
        return v


class ChunkingConfig(BaseModel):
    chunk_size: int = 1000
    chunk_overlap: int = 200

    @field_validator("chunk_size")
    @classmethod
    def chunk_size_positive(cls, v: int) -> int:
        if v <= 0:
            raise ValueError("chunk_size must be positive")
        return v

    @model_validator(mode="after")
    def overlap_less_than_size(self) -> ChunkingConfig:
        if self.chunk_overlap >= self.chunk_size:
            raise ValueError("chunk_overlap must be less than chunk_size")
        return self


class VectorStoreConfig(BaseModel):
    persist_dir: str = "data/chroma"
    collection_name: str = "helpdesk_docs"


class RetrievalConfig(BaseModel):
    top_k: int = 4
    method: Literal["vector", "bm25", "hybrid"] = "hybrid"
    min_score: float = 0.3

    @field_validator("top_k")
    @classmethod
    def top_k_at_least_one(cls, v: int) -> int:
        if v < 1:
            raise ValueError("top_k must be at least 1")
        return v

    @field_validator("min_score")
    @classmethod
    def min_score_range(cls, v: float) -> float:
        if not 0.0 <= v <= 1.0:
            raise ValueError("min_score must be between 0.0 and 1.0")
        return v


class ChatConfig(BaseModel):
    max_history_turns: int = 4
    max_context_chars: int = 6000

    @field_validator("max_history_turns")
    @classmethod
    def turns_non_negative(cls, v: int) -> int:
        if v < 0:
            raise ValueError("max_history_turns must be non-negative")
        return v

    @field_validator("max_context_chars")
    @classmethod
    def context_chars_positive(cls, v: int) -> int:
        if v < 100:
            raise ValueError("max_context_chars must be at least 100")
        return v


class RAGConfig(BaseModel):
    ollama: OllamaConfig = OllamaConfig()
    chunking: ChunkingConfig = ChunkingConfig()
    vector_store: VectorStoreConfig = VectorStoreConfig()
    retrieval: RetrievalConfig = RetrievalConfig()
    chat: ChatConfig = ChatConfig()


def load_config(config_path: str = "config.yaml") -> RAGConfig:
    path = Path(config_path)
    data: dict = {}
    if path.exists():
        with open(path) as f:
            data = yaml.safe_load(f) or {}
        logger.debug("Loaded config from %s", path)
    else:
        logger.warning("Config file %s not found, using defaults", path)

    # Env var overrides
    env_overrides = {
        "OLLAMA_BASE_URL": ("ollama", "base_url"),
        "OLLAMA_EMBEDDING_MODEL": ("ollama", "embedding_model"),
        "OLLAMA_LLM_MODEL": ("ollama", "llm_model"),
        "OLLAMA_TEMPERATURE": ("ollama", "temperature"),
        "OLLAMA_MAX_TOKENS": ("ollama", "max_tokens"),
        "CHUNK_SIZE": ("chunking", "chunk_size"),
        "CHUNK_OVERLAP": ("chunking", "chunk_overlap"),
        "RETRIEVAL_TOP_K": ("retrieval", "top_k"),
        "RETRIEVAL_MIN_SCORE": ("retrieval", "min_score"),
        "MAX_CONTEXT_CHARS": ("chat", "max_context_chars"),
        "MAX_HISTORY_TURNS": ("chat", "max_history_turns"),
    }
    type_coercions = {
        "OLLAMA_TEMPERATURE": float,
        "OLLAMA_MAX_TOKENS": int,
        "CHUNK_SIZE": int,
        "CHUNK_OVERLAP": int,
        "RETRIEVAL_TOP_K": int,
        "RETRIEVAL_MIN_SCORE": float,
        "MAX_CONTEXT_CHARS": int,
        "MAX_HISTORY_TURNS": int,
    }
    for env_var, (section, key) in env_overrides.items():
        value = os.environ.get(env_var)
        if value is not None:
            coerced = type_coercions.get(env_var, str)(value)
            data.setdefault(section, {})[key] = coerced
            logger.debug("Override %s=%s from env var", key, coerced)

    config = RAGConfig(**data)
    logger.info("Config loaded: llm=%s, retrieval=%s/%s, top_k=%s", config.ollama.llm_model, config.retrieval.method, config.retrieval.min_score, config.retrieval.top_k)
    return config