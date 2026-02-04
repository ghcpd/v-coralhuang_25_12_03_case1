"""User display package: fast, modular, extensible."""

from .store import UserStore
from .formatters import format_user, format_users
from .filters import filter_users as apply_filters, SimpleCriteriaFilter
from .config import Config, get_config, DEFAULT_CONFIG, DEFAULT_REQUIRED_FIELDS, default_validator
from .metrics import metrics, Metrics
from .logging_utils import get_logger, LOG_MARKER
from .errors import UserDisplayError, ValidationError, UserNotFoundError

__all__ = [
    "UserStore",
    "format_user",
    "format_users",
    "apply_filters",
    "SimpleCriteriaFilter",
    "Config",
    "get_config",
    "DEFAULT_CONFIG",
    "DEFAULT_REQUIRED_FIELDS",
    "default_validator",
    "metrics",
    "Metrics",
    "get_logger",
    "LOG_MARKER",
    "UserDisplayError",
    "ValidationError",
    "UserNotFoundError",
]
