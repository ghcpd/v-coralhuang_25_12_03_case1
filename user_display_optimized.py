"""Optimized, modular implementation preserving the baseline public API."""

from typing import Dict, Iterable, Optional

from user_display.store import UserStore
from user_display.config import Config, default_config
from user_display.metrics import Metrics
from user_display.logging_utils import get_logger


# Public API compatibility
__all__ = [
    "display_users",
    "get_user_by_id",
    "filter_users",
    "export_users_to_string",
]


def _build_store(
    users: Iterable[dict],
    config: Optional[Config] = None,
    metrics: Optional[Metrics] = None,
    logger=None,
    enable_cache: Optional[bool] = None,
) -> UserStore:
    cfg = config or default_config()
    return UserStore(users, config=cfg, metrics=metrics, logger=logger, enable_cache=enable_cache)


# Extended optional args keep backward compatibility when called with original signature

def display_users(
    users: Iterable[dict],
    show_all: bool = True,
    verbose: bool = False,
    *,
    formatter: Optional[str] = None,
    include_fields=None,
    exclude_fields=None,
    config: Optional[Config] = None,
    metrics: Optional[Metrics] = None,
    logger=None,
    enable_cache: Optional[bool] = None,
) -> str:
    store = _build_store(users, config=config, metrics=metrics, logger=logger, enable_cache=enable_cache)
    return store.display_users(show_all=show_all, verbose=verbose, formatter=formatter, include_fields=include_fields, exclude_fields=exclude_fields)


def get_user_by_id(
    users: Iterable[dict],
    user_id,
    *,
    config: Optional[Config] = None,
    metrics: Optional[Metrics] = None,
    logger=None,
) -> Optional[dict]:
    store = _build_store(users, config=config, metrics=metrics, logger=logger)
    return store.get_user_by_id(user_id)


def filter_users(
    users: Iterable[dict],
    criteria: Dict,
    *,
    strategy: str = "default",
    case_sensitive: Optional[bool] = None,
    use_cache: Optional[bool] = None,
    config: Optional[Config] = None,
    metrics: Optional[Metrics] = None,
    logger=None,
) -> list:
    store = _build_store(users, config=config, metrics=metrics, logger=logger)
    return store.filter_users(criteria, strategy=strategy, case_sensitive=case_sensitive, use_cache=use_cache)


def export_users_to_string(
    users: Iterable[dict],
    *,
    include_fields=None,
    exclude_fields=None,
    config: Optional[Config] = None,
    metrics: Optional[Metrics] = None,
    logger=None,
) -> str:
    store = _build_store(users, config=config, metrics=metrics, logger=logger)
    return store.export_users_to_string(include_fields=include_fields, exclude_fields=exclude_fields)


# Sample data for manual demonstration
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
    print(display_users(sample_users))
    print(get_user_by_id(sample_users, 1))
    print(filter_users(sample_users, {"role": "Admin"}))
    print(export_users_to_string(sample_users))
