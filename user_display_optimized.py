"""Optimized user display module with preserved public API."""

from typing import Any, Mapping, Iterable, Sequence, Optional

from user_display.store import UserStore
from user_display.formatters import format_users
from user_display.filters import filter_users as core_filter
from user_display.config import get_config
from user_display.logging_utils import get_logger
from user_display.metrics import metrics

logger = get_logger(__name__)


def display_users(
    users: Iterable[Mapping[str, Any]],
    show_all: bool = True,
    verbose: bool = False,
    formatter: Optional[str] = None,
    include: Optional[Sequence[str]] = None,
    exclude: Optional[Sequence[str]] = None,
) -> str:
    cfg = get_config({"default_formatter": "verbose" if verbose else "compact"})
    store = UserStore(users, config=cfg, logger=logger, metrics=metrics)
    mode = formatter or cfg.default_formatter
    text = format_users(store.iter_users(), mode=mode, include=include, exclude=exclude, show_total=show_all)
    return text


def get_user_by_id(users: Iterable[Mapping[str, Any]], user_id: Any):
    store = UserStore(users, logger=logger, metrics=metrics)
    return store.get_by_id(user_id)


def filter_users(
    users: Iterable[Mapping[str, Any]],
    criteria: Mapping[str, Any],
    case_insensitive: bool = True,
    strategy=None,
):
    store = UserStore(users, logger=logger, metrics=metrics)
    return store.filter(criteria, case_insensitive=case_insensitive, strategy=strategy)


def export_users_to_string(
    users: Iterable[Mapping[str, Any]],
    formatter: str = "verbose",
    include: Optional[Sequence[str]] = None,
    exclude: Optional[Sequence[str]] = None,
) -> str:
    store = UserStore(users, logger=logger, metrics=metrics)
    header = "USER_EXPORT_START\n" + "=" * 80 + "\n"
    body = format_users(store.iter_users(), mode=formatter, include=include, exclude=exclude, show_total=False)
    footer = "\nUSER_EXPORT_END"
    return header + body + footer


# Sample data for manual testing and demonstration
sample_users = [
    {
        "id": 1,
        "name": "John Doe",
        "email": "john@example.com",
        "role": "Admin",
        "status": "Active",
        "join_date": "2023-01-15",
        "last_login": "2025-11-26",
    },
    {
        "id": 2,
        "name": "Jane Smith",
        "email": "jane@example.com",
        "role": "User",
        "status": "Inactive",
        "join_date": "2023-06-20",
        "last_login": "2025-11-20",
    },
]


if __name__ == "__main__":
    print("Optimized Implementation Output")
    print("=" * 80)
    print(display_users(sample_users))
    print("Single user lookup (id=1)")
    print(get_user_by_id(sample_users, 1))
    print("Filter users by role=User")
    print(filter_users(sample_users, {"role": "User"}))
    print("Export users")
    print(export_users_to_string(sample_users))
