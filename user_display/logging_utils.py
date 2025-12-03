"""Utility logging helpers for user_display.

Provides a package-scoped logger that prefixes messages with [MARKER].
"""
import logging

_logger = None


def get_logger(name: str = "user_display") -> logging.Logger:
    global _logger
    if _logger:
        return _logger

    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter("[MARKER] %(levelname)s %(message)s")
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    logger.setLevel(logging.INFO)
    _logger = logger
    return logger
