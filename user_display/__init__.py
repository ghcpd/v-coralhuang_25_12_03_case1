"""User Display Module - High-Performance, Modular, Extensible.

This package provides efficient user data management and display
with O(1) lookups, pluggable formatters, and extensible filtering.
"""

from .store import UserStore
from .formatters import (
    BaseFormatter,
    CompactFormatter,
    VerboseFormatter,
    JSONLikeFormatter,
)
from .filters import FilterStrategy, MultiCriteriaFilter
from .config import Config
from .errors import UserDisplayError, ValidationError, UserNotFoundError
from .metrics import Metrics

__version__ = "2.0.0"

__all__ = [
    "UserStore",
    "BaseFormatter",
    "CompactFormatter",
    "VerboseFormatter",
    "JSONLikeFormatter",
    "FilterStrategy",
    "MultiCriteriaFilter",
    "Config",
    "UserDisplayError",
    "ValidationError",
    "UserNotFoundError",
    "Metrics",
]
