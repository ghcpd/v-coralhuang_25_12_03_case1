"""Logging utilities with centralized marker-based logging."""

import logging
from typing import Optional


_logger: Optional[logging.Logger] = None
_MARKER = "[UserDisplay]"


def get_logger(name: str = "user_display") -> logging.Logger:
    """Get or create the logger with standardized marker."""
    global _logger
    if _logger is None:
        _logger = logging.getLogger(name)
        if not _logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                f"{_MARKER} %(levelname)s - %(message)s"
            )
            handler.setFormatter(formatter)
            _logger.addHandler(handler)
            _logger.setLevel(logging.INFO)
    return _logger


def log_info(message: str) -> None:
    """Log an info message with marker."""
    get_logger().info(message)


def log_warning(message: str) -> None:
    """Log a warning message with marker."""
    get_logger().warning(message)


def log_error(message: str) -> None:
    """Log an error message with marker."""
    get_logger().error(message)


def log_debug(message: str) -> None:
    """Log a debug message with marker."""
    get_logger().debug(message)
