"""Tests for helpdesk_rag.engine."""

from helpdesk_rag.engine import _format_history, _truncate_context


class TestFormatHistory:
    def test_none_history(self):
        assert _format_history(None, 4) == "(No previous conversation)"

    def test_empty_history(self):
        assert _format_history([], 4) == "(No previous conversation)"

    def test_truncation(self):
        history = [{"role": "user", "content": f"msg{i}"} for i in range(20)]
        result = _format_history(history, 2)
        # Should only include last 4 messages (2 turns * 2)
        assert "msg18" in result
        assert "msg19" in result
        assert "msg0" not in result


class TestTruncateContext:
    def test_short_context_unchanged(self):
        assert _truncate_context("short", 100) == "short"

    def test_truncates_at_line_boundary(self):
        context = "line1\nline2\nline3"
        result = _truncate_context(context, 8)
        assert result.endswith("\n")

    def test_truncates_at_sentence_boundary(self):
        context = "First sentence. Second sentence. Third sentence."
        result = _truncate_context(context, 25)
        assert result.endswith(". ") or result.endswith(".")