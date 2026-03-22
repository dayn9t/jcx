"""Structured logging configuration using loguru.

This module provides a centralized logging configuration that supports both
human-readable output for development and JSON-structured output for production
log aggregation.

Usage:
    from jcx.util.logging_config import configure_logging

    # Development (default)
    configure_logging()

    # Production with JSON output
    configure_logging(json_format=True, level="INFO")
"""

import json
import sys

from loguru import logger


def configure_logging(
    json_format: bool = False,
    level: str = "INFO",
    *,
    sink: object | None = None,
) -> None:
    """Configure loguru for structured logging.

    Args:
        json_format: If True, output JSON-formatted logs for production.
                     If False, output human-readable logs for development.
        level: Minimum log level to capture (DEBUG, INFO, WARNING, ERROR, CRITICAL).
        sink: Optional custom sink for testing. Defaults to sys.stderr.

    Example:
        >>> configure_logging()  # Development mode
        >>> configure_logging(json_format=True)  # Production mode

    """
    # Remove default handler
    logger.remove()

    output = sink if sink is not None else sys.stderr

    if json_format:

        def json_sink(message: object) -> None:
            """Sink that formats log records as JSON."""
            record = message.record
            log_entry = {
                "timestamp": record["time"].isoformat(),
                "level": record["level"].name,
                "message": record["message"],
                "module": record["module"],
                "function": record["function"],
                "line": record["line"],
            }
            # Add extra context if present
            if record["extra"]:
                log_entry["extra"] = record["extra"]
            # Add exception info if present
            if record["exception"]:
                log_entry["exception"] = str(record["exception"])
            print(json.dumps(log_entry), file=output)

        logger.add(json_sink, level=level)
    else:
        # Human-readable format for development
        logger.add(
            output,
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
            level=level,
        )


from loguru import Logger

from loguru import logger


def get_logger() -> Logger:
    """Get the configured logger instance.

    Returns:
        The loguru logger instance for direct use.

    Example:
        >>> from jcx.util.logging_config import get_logger
        >>> log = get_logger()
        >>> log.info("Application started")

    """
    return logger
