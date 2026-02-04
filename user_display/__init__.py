"""User display package - high-performance, modular, extensible user management."""

from .store import UserStore
from .formatters import Formatter, get_formatter
from .filters import FilterStrategy, create_criteria_filter
from .config import Config, get_config, set_config, reset_config
from .logging_utils import get_logger
from .metrics import get_metrics, reset_metrics
from .errors import UserDisplayError, UserNotFoundError, InvalidUserDataError, ValidationError

__all__ = [
    "UserStore",
    "Formatter",
    "get_formatter",
    "FilterStrategy",
    "create_criteria_filter",
    "Config",
    "get_config",
    "set_config",
    "reset_config",
    "get_logger",
    "get_metrics",
    "reset_metrics",
    "UserDisplayError",
    "UserNotFoundError",
    "InvalidUserDataError",
    "ValidationError",
]

__version__ = "1.0.0"
