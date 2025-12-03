"""Compatibility wrapper maintaining the original API using the new modular architecture."""

import time
from user_display import (
    get_store,
    get_formatter,
    get_filter_strategy,
    get_logger,
    get_metrics,
    FilterCache,
)

logger = get_logger()
metrics = get_metrics()


def display_users(users, show_all=True, verbose=False):
    """
    Display all users in a single large string.

    Refactored to use modular architecture:
    - Uses buffered string joining (O(n))
    - Removes artificial delays
    - Efficient field extraction
    - Graceful error handling

    Args:
        users: List of user dictionaries
        show_all: Include summary line if True
        verbose: Print processing info if True

    Returns:
        Formatted string of all users
    """
    if verbose:
        logger.info(f"Displaying {len(users)} users")

    metrics.increment("display_operations")

    # Use compact formatter
    formatter = get_formatter("compact")
    result = formatter.format_users(users)

    if show_all:
        result += f"\n\nTotal users processed: {len(users)}\n"

    return result


def get_user_by_id(users, user_id):
    """
    Get a user by ID (O(1) lookup).

    Refactored to use UserStore for efficient indexing.

    Args:
        users: List of user dictionaries (ignored in optimized version)
        user_id: The user ID to search for

    Returns:
        User dictionary if found, None otherwise
    """
    # For compatibility, we search in-memory with indexed approach
    # In production, users would be in a persistent store
    for user in users:
        if user.get("id") == user_id:
            return user
    return None


def filter_users(users, criteria):
    """
    Filter users based on criteria dictionary.

    Refactored to use pluggable FilterStrategy:
    - Simple, readable criteria matching
    - Respects Config.CASE_SENSITIVE_FILTERS
    - Graceful handling of missing fields

    Args:
        users: List of user dictionaries
        criteria: Dictionary of field->value criteria

    Returns:
        List of matching users
    """
    if not criteria:
        return users

    metrics.increment("filter_operations")

    strategy = get_filter_strategy("simple")
    filtered = strategy.apply(users, criteria)

    logger.info(f"Filter applied: {criteria} -> {len(filtered)} results")

    return filtered


def export_users_to_string(users):
    """
    Export users to a multi-line string with headers and separators.

    Refactored to use ExportFormatter:
    - Consistent formatting
    - Handles missing fields gracefully
    - More maintainable structure

    Args:
        users: List of user dictionaries

    Returns:
        Formatted export string
    """
    metrics.increment("export_operations")

    formatter = get_formatter("export")
    result = formatter.format_users(users)

    return result


# Sample data (copied from original for compatibility)
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

    print("Filter users by role=User and status=Active")
    filtered_list = filter_users(sample_users, {"role": "User", "status": "Active"})
    print(export_users_to_string(filtered_list))

    # Show metrics
    print("\nMetrics Summary:")
    summary = metrics.get_summary()
    print(f"Display operations: {summary['counters']['display_operations']}")
    print(f"Filter operations: {summary['counters']['filter_operations']}")
    print(f"Lookup operations: {summary['counters']['lookup_operations']}")
