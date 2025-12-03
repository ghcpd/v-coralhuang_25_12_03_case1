import logging
import sys
from typing import Optional


_LOGGER_NAME = "user_display"
_DEFAULT_MARKER = "[MARKER]"


def get_logger(marker: str = _DEFAULT_MARKER, level: int = logging.INFO) -> logging.Logger:
    """Return a configured logger with marker prefix."""
    logger = logging.getLogger(_LOGGER_NAME)
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(f"{marker} %(asctime)s - %(levelname)s - %(message)s")
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(level)
    # Allow propagation so external handlers (e.g., pytest caplog) can capture messages
    logger.propagate = True
    return logger


def log_validation_error(logger: Optional[logging.Logger], message: str) -> None:
    if logger:
        logger.warning(message)
