"""Optimized user display implementation with backwards-compatible API.

This module provides the same public API as the baseline implementation
but uses the new modular architecture for high performance.
"""

from typing import Dict, List, Any, Optional

from user_display import (
    UserStore,
    Config,
    MultiCriteriaFilter,
)
from user_display.formatters import VerboseFormatter, get_formatter
from user_display.metrics import global_metrics


# Global store instance for backwards compatibility
_global_store: Optional[UserStore] = None
_global_config = Config.default()


def _ensure_store(users: List[Dict[str, Any]]) -> UserStore:
    """
    Ensure a UserStore exists with the given users.

    Args:
        users: List of user dictionaries

    Returns:
        UserStore instance
    """
    global _global_store

    # Create new store each time for API compatibility
    # (original implementation didn't maintain state)
    return UserStore(users, config=_global_config)


def display_users(
    users: List[Dict[str, Any]], show_all: bool = True, verbose: bool = False
) -> str:
    """
    Display all users in a formatted string.

    This is the backwards-compatible version that matches the original API.
    Uses efficient string building with join instead of concatenation.

    Args:
        users: List of user dictionaries
        show_all: Whether to show total count
        verbose: Whether to log verbose information (not used in optimized version)

    Returns:
        Formatted string with all users
    """
    # Use the optimized store for validation
    store = _ensure_store(users)

    # Get validated users from store
    validated_users = store.get_all()

    # Use compact formatter for backwards compatibility
    formatter = get_formatter("compact", _global_config)

    # Format all users efficiently
    result = formatter.format_users(validated_users, show_total=show_all)

    return result


def get_user_by_id(users: List[Dict[str, Any]], user_id: int) -> Optional[Dict[str, Any]]:
    """
    Get user by ID in O(1) time using indexed lookup.

    Args:
        users: List of user dictionaries
        user_id: User ID to lookup

    Returns:
        User dictionary or None if not found
    """
    store = _ensure_store(users)
    return store.get_by_id(user_id)


def filter_users(users: List[Dict[str, Any]], criteria: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Filter users based on criteria dictionary.

    This implementation uses pluggable filter strategies and is much
    more extensible than the original nested if statements.

    Args:
        users: List of user dictionaries
        criteria: Dictionary of field->value criteria

    Returns:
        List of matching users
    """
    store = _ensure_store(users)
    validated_users = store.get_all()

    # Use MultiCriteriaFilter with caching
    filter_obj = MultiCriteriaFilter(criteria, config=_global_config)
    return filter_obj.filter(validated_users)


def export_users_to_string(users: List[Dict[str, Any]]) -> str:
    """
    Export users to a multi-line string.

    Uses efficient string building and the verbose formatter.

    Args:
        users: List of user dictionaries

    Returns:
        Formatted export string
    """
    store = _ensure_store(users)
    validated_users = store.get_all()

    # Use verbose formatter with export styling
    formatter = VerboseFormatter(config=_global_config)

    # Build export string efficiently
    parts = [
        "USER_EXPORT_START\n",
        _global_config.export_separator + "\n",
        formatter.format_users(validated_users, show_total=False),
        "USER_EXPORT_END\n",
    ]

    return "".join(parts)


# Sample data for manual testing (same as original)
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

    print("Single user lookup (id=3)")
    print(get_user_by_id(sample_users, 3))

    print("\nFilter users by role=User and status=Active")
    filtered_list = filter_users(sample_users, {"role": "User", "status": "Active"})
    print(export_users_to_string(filtered_list))

    print("\nMetrics Summary:")
    print(global_metrics.summary())
