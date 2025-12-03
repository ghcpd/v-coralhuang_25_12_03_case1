"""Logging utilities for the user_display module."""

import logging
import sys
from .config import Config


class ModuleLogger:
    """Unified logger for the user_display module."""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self._initialized = True
        self.logger = logging.getLogger("user_display")
        self.logger.setLevel(logging.DEBUG)

        if not self.logger.handlers:
            handler = logging.StreamHandler(sys.stdout)
            formatter = logging.Formatter(
                f"%(asctime)s - {Config.LOG_MARKER} - %(levelname)s - %(message)s"
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)

    def debug(self, message):
        """Log debug message."""
        if Config.ENABLE_LOGGING:
            self.logger.debug(message)

    def info(self, message):
        """Log info message."""
        if Config.ENABLE_LOGGING:
            self.logger.info(message)

    def warning(self, message):
        """Log warning message."""
        if Config.ENABLE_LOGGING:
            self.logger.warning(message)

    def error(self, message):
        """Log error message."""
        if Config.ENABLE_LOGGING:
            self.logger.error(message)


def get_logger():
    """Get the global module logger instance."""
    return ModuleLogger()
