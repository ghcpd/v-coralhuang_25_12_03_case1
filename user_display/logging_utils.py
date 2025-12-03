"""Centralized logging utilities with [MARKER] support."""

import logging
import sys
from typing import Optional


class MarkedLogger:
    """Logger wrapper that adds [MARKER] prefix to all messages."""

    def __init__(self, name: str, marker: str = "MARKER"):
        self.logger = logging.getLogger(name)
        self.marker = marker

    def _format_message(self, msg: str) -> str:
        """Add marker prefix to message."""
        return f"[{self.marker}] {msg}"

    def debug(self, msg: str, *args, **kwargs):
        """Log debug message with marker."""
        self.logger.debug(self._format_message(msg), *args, **kwargs)

    def info(self, msg: str, *args, **kwargs):
        """Log info message with marker."""
        self.logger.info(self._format_message(msg), *args, **kwargs)

    def warning(self, msg: str, *args, **kwargs):
        """Log warning message with marker."""
        self.logger.warning(self._format_message(msg), *args, **kwargs)

    def error(self, msg: str, *args, **kwargs):
        """Log error message with marker."""
        self.logger.error(self._format_message(msg), *args, **kwargs)

    def critical(self, msg: str, *args, **kwargs):
        """Log critical message with marker."""
        self.logger.critical(self._format_message(msg), *args, **kwargs)


def setup_logger(
    name: str,
    level: int = logging.INFO,
    marker: str = "MARKER",
    handler: Optional[logging.Handler] = None,
) -> MarkedLogger:
    """
    Setup a marked logger with consistent formatting.

    Args:
        name: Logger name
        level: Logging level
        marker: Marker prefix for messages
        handler: Optional custom handler

    Returns:
        MarkedLogger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Remove existing handlers to avoid duplicates
    logger.handlers.clear()

    if handler is None:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(formatter)

    logger.addHandler(handler)
    logger.propagate = False

    return MarkedLogger(name, marker)


# Default logger for the module
default_logger = setup_logger("user_display", level=logging.WARNING)
