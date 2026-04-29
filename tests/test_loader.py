"""Tests for helpdesk_rag.loader."""

import tempfile
from pathlib import Path

import pytest

from helpdesk_rag.exceptions import DocumentLoadError
from helpdesk_rag.loader import load_document, SUPPORTED_EXTENSIONS


class TestLoadDocument:
    def test_load_text_file(self, tmp_path: Path):
        f = tmp_path / "test.txt"
        f.write_text("Hello world", encoding="utf-8")
        doc = load_document(f)
        assert doc.content == "Hello world"
        assert doc.metadata["source"] == "test.txt"
        assert doc.metadata["format"] == "text"

    def test_load_markdown_file(self, tmp_path: Path):
        f = tmp_path / "test.md"
        f.write_text("# Title\n\nSome content\n\n## Section\nMore content", encoding="utf-8")
        doc = load_document(f)
        assert "Title" in doc.content
        assert doc.metadata["format"] == "markdown"
        assert "Title" in doc.metadata.get("headings", [])

    def test_unsupported_extension(self, tmp_path: Path):
        f = tmp_path / "test.xyz"
        f.write_text("data", encoding="utf-8")
        with pytest.raises(DocumentLoadError, match="Unsupported"):
            load_document(f)

    def test_nonexistent_file(self):
        with pytest.raises(DocumentLoadError, match="not found"):
            load_document("/nonexistent/path/file.txt")

    def test_supported_extensions(self):
        assert ".pdf" in SUPPORTED_EXTENSIONS
        assert ".docx" in SUPPORTED_EXTENSIONS
        assert ".md" in SUPPORTED_EXTENSIONS
        assert ".txt" in SUPPORTED_EXTENSIONS