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

import sys
from typing import TYPE_CHECKING, TextIO

from loguru import logger

if TYPE_CHECKING:
    from loguru import Logger


def configure_logging(
    json_format: bool = False,
    level: str = "INFO",
    *,
    sink: TextIO | None = None,
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

    output: TextIO = sink if sink is not None else sys.stderr

    if json_format:
        # Use loguru's built-in serialize option for JSON format
        logger.add(output, level=level, serialize=True)
    else:
        # Human-readable format for development
        logger.add(
            output,
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
            level=level,
        )


def get_logger() -> "Logger":
    """Get the configured logger instance.

    Returns:
        The loguru logger instance for direct use.

    Example:
        >>> from jcx.util.logging_config import get_logger
        >>> log = get_logger()
        >>> log.info("Application started")

    """
    return logger
