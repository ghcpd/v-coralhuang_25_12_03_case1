"""Compatibility wrapper exposing the same public API as the baseline but using
the new modular, performant implementation under the hood.
"""
from user_display.store import UserStore
from user_display.formatters import format_users, format_user
from user_display.filters import CriteriaFilter
from user_display.logging_utils import get_logger
from user_display.metrics import metrics

logger = get_logger(__name__)


def _ensure_users_list(users):
    # Accept iterable; convert to list for multiple passes.
    return list(users) if users is not None else []


def display_users(users, show_all=True, verbose=False):
    """Return a formatted string of users (fast implementation).

    Keeps same signature as the baseline. `verbose` maps to verbose formatter.
    """
    users = _ensure_users_list(users)
    metrics.inc("display_calls")

    mode = "verbose" if verbose else "compact"
    store = UserStore(users, validate=False, cache_filters=True)
    out = format_users(store.iter(), mode=mode, show_all=show_all)
    logger.info("display_users: processed=%d", len(users))
    return out


def get_user_by_id(users, user_id):
    """O(1) lookup by id using an index map."""
    users = _ensure_users_list(users)
    store = UserStore(users, validate=False)
    metrics.inc("get_by_id_calls")
    res = store.get_by_id(user_id)
    logger.info("get_user_by_id: id=%r found=%s", user_id, bool(res))
    return res


def filter_users(users, criteria):
    """Filter users based on criteria dict. Returns a list of matching users.

    Keeps same signature as the baseline and supports substring matching for
    name/email and exact match for other fields.
    """
    users = _ensure_users_list(users)
    metrics.inc("filter_calls")
    store = UserStore(users, validate=False, cache_filters=True)
    results = store.filter(criteria=criteria)
    logger.info("filter_users: criteria=%r matched=%d", criteria, len(results))
    return results


def export_users_to_string(users):
    """Export users into a consistent string format (verbose-like).

    Similar to the baseline but efficient and robust to missing fields.
    """
    users = _ensure_users_list(users)
    metrics.inc("export_calls")
    store = UserStore(users, validate=False)
    lines = []
    lines.append("USER_EXPORT_START")
    lines.append("=" * 80)
    for u in store.iter():
        lines.append(format_user(u, mode="verbose"))
        lines.append("-" * 80)

    lines.append("USER_EXPORT_END")
    out = "\n".join(lines)
    logger.info("export_users_to_string: exported=%d", len(users))
    return out


if __name__ == "__main__":
    # if executed directly, show a quick demonstration using the original
    from user_display_original import sample_users

    print(display_users(sample_users))
    print(get_user_by_id(sample_users, 3))
    print(filter_users(sample_users, {"role": "User", "status": "Active"}))
    print(export_users_to_string(sample_users))
