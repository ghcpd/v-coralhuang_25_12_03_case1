"""User display module - high-performance, modular, extensible."""

from .store import UserStore, get_store
from .formatters import get_formatter, CompactFormatter, VerboseFormatter, JSONFormatter, ExportFormatter
from .filters import get_filter_strategy, FilterCache
from .config import Config
from .logging_utils import get_logger
from .metrics import get_metrics
from .errors import UserDisplayError, MalformedUserError, ValidationError, FilterError

__version__ = "2.0.0"
__all__ = [
    "UserStore",
    "get_store",
    "get_formatter",
    "CompactFormatter",
    "VerboseFormatter",
    "JSONFormatter",
    "ExportFormatter",
    "get_filter_strategy",
    "FilterCache",
    "Config",
    "get_logger",
    "get_metrics",
    "UserDisplayError",
    "MalformedUserError",
    "ValidationError",
    "FilterError",
]
