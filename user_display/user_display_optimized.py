"""Optimized user display module providing same public functions as baseline.

Internally uses UserStore, formatters, filters, and metrics.
"""
from .store import UserStore
from .formatters import format_compact, format_verbose, format_json_like
from .config import DEFAULTS
from .logging_utils import get_logger

logger = get_logger(__name__)


def _make_store(users, case_sensitive=None, cache_enabled=None):
    if case_sensitive is None:
        case_sensitive = DEFAULTS["case_sensitive"]
    if cache_enabled is None:
        cache_enabled = DEFAULTS["cache_enabled"]
    return UserStore(users=users, case_sensitive=case_sensitive, cache_enabled=cache_enabled)


def display_users(users, show_all=True, verbose=False, formatter=None, fields=None):
    """Return a string display of users.

    Backwards-compatible signature preserved; extra params supported.
    """
    store = _make_store(users)
    lines = []
    fmt = formatter or DEFAULTS["formatter"]

    for u in store:
        if verbose:
            logger.info("Processing user: %s", u.get("id"))
        if fmt == "compact":
            lines.append(format_compact(u, fields))
        elif fmt == "verbose":
            lines.append(format_verbose(u, fields))
        elif fmt == "json":
            lines.append(format_json_like(u, fields))
        else:
            lines.append(format_compact(u, fields))

    if show_all:
        lines.append("")
        lines.append("Total users processed: %d" % len(lines))

    return "\n".join(lines)


def get_user_by_id(users, user_id):
    store = _make_store(users)
    return store.get_user_by_id(user_id)


def filter_users(users, criteria):
    store = _make_store(users)
    return store.filter_users(criteria)


def export_users_to_string(users, formatter="verbose", fields=None):
    store = _make_store(users)
    header = "USER_EXPORT_START\n" + ("=" * 80) + "\n"
    parts = [header]
    for u in store:
        if formatter == "compact":
            parts.append(format_compact(u, fields) + "\n")
        elif formatter == "json":
            parts.append(format_json_like(u, fields) + "\n")
        else:
            parts.append(format_verbose(u, fields) + "\n")
        parts.append(("-" * 80) + "\n")

    parts.append("USER_EXPORT_END\n")
    return "".join(parts)
