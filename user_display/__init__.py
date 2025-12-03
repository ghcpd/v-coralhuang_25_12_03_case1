"""High-level user_display package API.

Expose a minimal API and useful helpers.
"""
from .store import UserStore
from .formatters import format_user, format_users
from .filters import CriteriaFilter
from .config import DEFAULT_CONFIG
from .logging_utils import get_logger
from .metrics import metrics

__all__ = [
    "UserStore",
    "format_user",
    "format_users",
    "CriteriaFilter",
    "DEFAULT_CONFIG",
    "get_logger",
    "metrics",
]
