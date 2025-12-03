"""
Optimized user display module with high-performance, modular design.

This module provides backward-compatible API with the baseline implementation
but uses optimized internals built on the modular package architecture.
"""

from typing import List, Dict, Any, Optional
import time

from user_display.store import UserStore
from user_display.formatters import get_formatter
from user_display.filters import create_criteria_filter
from user_display.logging_utils import log_info
from user_display.metrics import get_metrics


# Global store for API compatibility
_global_store: Optional[UserStore] = None


def _get_store() -> UserStore:
    """Get or create the global store."""
    global _global_store
    if _global_store is None:
        _global_store = UserStore()
    return _global_store


def display_users(users: List[Dict[str, Any]], show_all: bool = True, verbose: bool = False) -> str:
    """
    Display all users with optimized formatting.

    API compatible with baseline implementation but uses efficient
    buffered string building instead of concatenation.

    Args:
        users: List of user dictionaries
        show_all: Whether to show total count
        verbose: Whether to log processing info (for compatibility)

    Returns:
        Formatted user display string
    """
    metrics = get_metrics()
    store = UserStore(users)

    formatter = get_formatter("compact")
    result = formatter.format_users(store.get_all())

    metrics.increment("display_operations")

    if verbose:
        log_info(f"Processed {len(users)} users")

    return result


def get_user_by_id(users: List[Dict[str, Any]], user_id: Any) -> Optional[Dict[str, Any]]:
    """
    Get a user by ID with O(1) lookup.

    API compatible with baseline but uses indexed lookup instead of linear search.

    Args:
        users: List of user dictionaries
        user_id: ID to search for

    Returns:
        User dictionary or None if not found
    """
    metrics = get_metrics()
    store = UserStore(users)

    result = store.get_by_id(user_id)
    metrics.increment("id_lookup_operations")

    return result


def filter_users(users: List[Dict[str, Any]], criteria: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Filter users based on criteria with extensible strategy pattern.

    API compatible with baseline but uses pluggable filtering strategies.

    Args:
        users: List of user dictionaries
        criteria: Dictionary of filter criteria

    Returns:
        Filtered list of users
    """
    metrics = get_metrics()
    store = UserStore(users)

    filter_strategy = create_criteria_filter(criteria)
    result = filter_strategy.apply(store.get_all())

    metrics.increment("filter_operations")

    return result


def export_users_to_string(users: List[Dict[str, Any]]) -> str:
    """
    Export users to formatted string.

    API compatible with baseline but uses efficient formatter interface.

    Args:
        users: List of user dictionaries

    Returns:
        Formatted export string
    """
    metrics = get_metrics()
    store = UserStore(users)

    formatter = get_formatter("export")
    result = formatter.format_users(store.get_all())

    metrics.increment("export_operations")

    return result


# Sample data for testing
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
    {
        "id": 3,
        "name": "Bob Johnson",
        "email": "bob@example.com",
        "role": "Moderator",
        "status": "Active",
        "join_date": "2024-02-10",
        "last_login": "2025-11-25",
    },
    {
        "id": 4,
        "name": "Alice Williams",
        "email": "alice@example.com",
        "role": "User",
        "status": "Active",
        "join_date": "2024-05-12",
        "last_login": "2025-11-26",
    },
    {
        "id": 5,
        "name": "Charlie Brown",
        "email": "charlie@example.com",
        "role": "User",
        "status": "Active",
        "join_date": "2024-08-03",
        "last_login": "2025-11-24",
    },
]


if __name__ == "__main__":
    print("Optimized Implementation Output")
    print("=" * 80)
    text = display_users(sample_users, show_all=True, verbose=False)
    print(text)

    print("\nSingle user lookup (id=3)")
    print(get_user_by_id(sample_users, 3))

    print("\nFilter users by role=User and status=Active")
    filtered_list = filter_users(sample_users, {"role": "User", "status": "Active"})
    print(export_users_to_string(filtered_list))
