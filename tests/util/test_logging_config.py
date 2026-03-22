"""Tests for logging configuration module."""

import io
import json

import pytest

from jcx.util.logging_config import configure_logging, get_logger


class TestConfigureLogging:
    """Tests for configure_logging function."""

    def test_text_format_output(self) -> None:
        """Text format produces human-readable output."""
        sink = io.StringIO()
        configure_logging(json_format=False, level="INFO", sink=sink)

        log = get_logger()
        log.info("Test message")

        output = sink.getvalue()
        assert "Test message" in output
        assert "INFO" in output
        # Should have timestamp and location info
        assert "|" in output

    def test_json_format_output(self) -> None:
        """JSON format produces valid JSON output."""
        sink = io.StringIO()
        configure_logging(json_format=True, level="INFO", sink=sink)

        log = get_logger()
        log.info("Test message")

        output = sink.getvalue().strip()
        # Should be valid JSON
        parsed = json.loads(output)
        assert parsed["message"] == "Test message"
        assert parsed["level"] == "INFO"
        assert "timestamp" in parsed
        assert "module" in parsed
        assert "function" in parsed
        assert "line" in parsed

    def test_json_format_includes_extra(self) -> None:
        """JSON format includes extra context."""
        sink = io.StringIO()
        configure_logging(json_format=True, level="INFO", sink=sink)

        log = get_logger()
        log.bind(user_id="123").info("User action")

        output = sink.getvalue().strip()
        parsed = json.loads(output)
        assert "extra" in parsed
        assert parsed["extra"]["user_id"] == "123"

    def test_log_level_filtering(self) -> None:
        """Log level filters out lower-priority messages."""
        sink = io.StringIO()
        configure_logging(json_format=False, level="WARNING", sink=sink)

        log = get_logger()
        log.debug("Debug message")  # Should be filtered
        log.info("Info message")  # Should be filtered
        log.warning("Warning message")  # Should appear

        output = sink.getvalue()
        assert "Debug message" not in output
        assert "Info message" not in output
        assert "Warning message" in output

    def test_get_logger_returns_logger(self) -> None:
        """get_logger returns the loguru logger instance."""
        log = get_logger()
        # loguru logger has these methods
        assert hasattr(log, "info")
        assert hasattr(log, "debug")
        assert hasattr(log, "warning")
        assert hasattr(log, "error")
        assert hasattr(log, "critical")


class TestLoggingIntegration:
    """Integration tests for logging with existing code."""

    def test_logger_works_after_reconfiguration(self) -> None:
        """Logger works correctly after multiple reconfigurations."""
        sink1 = io.StringIO()
        configure_logging(json_format=False, level="INFO", sink=sink1)
        get_logger().info("First message")

        sink2 = io.StringIO()
        configure_logging(json_format=True, level="INFO", sink=sink2)
        get_logger().info("Second message")

        # First sink should only have first message
        assert "First message" in sink1.getvalue()
        assert "Second message" not in sink1.getvalue()

        # Second sink should only have second message (JSON)
        output2 = sink2.getvalue().strip()
        parsed = json.loads(output2)
        assert parsed["message"] == "Second message"
