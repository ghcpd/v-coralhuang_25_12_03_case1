"""User display package: high-performance, modular, extensible."""

from .store import UserStore
from .formatters import get_formatter, register_formatter
from .filters import register_strategy, get_strategy
from .config import Config, DEFAULT_FIELDS, default_config
from .metrics import Metrics
from .errors import UserDisplayError, ValidationError, NotFoundError

__all__ = [
    "UserStore",
    "get_formatter",
    "register_formatter",
    "register_strategy",
    "get_strategy",
    "Config",
    "DEFAULT_FIELDS",
    "default_config",
    "Metrics",
    "UserDisplayError",
    "ValidationError",
    "NotFoundError",
]
