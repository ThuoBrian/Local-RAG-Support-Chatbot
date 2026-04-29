"""Tests for helpdesk_rag.config."""

import os
import tempfile
from pathlib import Path

import pytest

from helpdesk_rag.config import (
    ChatConfig,
    ChunkingConfig,
    OllamaConfig,
    RAGConfig,
    RetrievalConfig,
    load_config,
)


class TestConfigDefaults:
    def test_ollama_defaults(self):
        cfg = OllamaConfig()
        assert cfg.llm_model == "glm-5.1:cloud"
        assert cfg.temperature == 0.3
        assert cfg.max_tokens == 768

    def test_retrieval_defaults(self):
        cfg = RetrievalConfig()
        assert cfg.top_k == 4
        assert cfg.min_score == 0.3

    def test_chat_defaults(self):
        cfg = ChatConfig()
        assert cfg.max_history_turns == 4
        assert cfg.max_context_chars == 6000

    def test_rag_config_composes(self):
        cfg = RAGConfig()
        assert cfg.ollama.llm_model == "glm-5.1:cloud"
        assert cfg.retrieval.top_k == 4


class TestConfigValidation:
    def test_chunk_overlap_ge_size_raises(self):
        with pytest.raises(ValueError, match="chunk_overlap"):
            ChunkingConfig(chunk_size=100, chunk_overlap=100)

    def test_chunk_overlap_gt_size_raises(self):
        with pytest.raises(ValueError, match="chunk_overlap"):
            ChunkingConfig(chunk_size=100, chunk_overlap=200)

    def test_chunk_size_zero_raises(self):
        with pytest.raises(ValueError, match="chunk_size"):
            ChunkingConfig(chunk_size=0, chunk_overlap=0)

    def test_top_k_zero_raises(self):
        with pytest.raises(ValueError, match="top_k"):
            RetrievalConfig(top_k=0)

    def test_min_score_negative_raises(self):
        with pytest.raises(ValueError, match="min_score"):
            RetrievalConfig(min_score=-0.1)

    def test_min_score_above_one_raises(self):
        with pytest.raises(ValueError, match="min_score"):
            RetrievalConfig(min_score=1.5)

    def test_temperature_above_two_raises(self):
        with pytest.raises(ValueError, match="temperature"):
            OllamaConfig(temperature=3.0)

    def test_max_tokens_zero_raises(self):
        with pytest.raises(ValueError, match="max_tokens"):
            OllamaConfig(max_tokens=0)

    def test_max_context_chars_too_small_raises(self):
        with pytest.raises(ValueError, match="max_context_chars"):
            ChatConfig(max_context_chars=10)


class TestLoadConfig:
    def test_load_from_yaml(self, tmp_path: Path):
        yaml_content = """
ollama:
  llm_model: "test-model"
retrieval:
  top_k: 2
"""
        config_file = tmp_path / "test.yaml"
        config_file.write_text(yaml_content)
        cfg = load_config(str(config_file))
        assert cfg.ollama.llm_model == "test-model"
        assert cfg.retrieval.top_k == 2

    def test_missing_yaml_uses_defaults(self, tmp_path: Path):
        cfg = load_config(str(tmp_path / "nonexistent.yaml"))
        assert cfg.ollama.llm_model == "glm-5.1:cloud"

    def test_env_var_override(self, monkeypatch: pytest.MonkeyPatch):
        monkeypatch.setenv("OLLAMA_LLM_MODEL", "env-model")
        monkeypatch.setenv("RETRIEVAL_TOP_K", "2")
        monkeypatch.setenv("RETRIEVAL_MIN_SCORE", "0.5")
        cfg = load_config()
        assert cfg.ollama.llm_model == "env-model"
        assert cfg.retrieval.top_k == 2
        assert cfg.retrieval.min_score == 0.5