"""
Example usage demonstrations for the refactored User Display Module.

This file shows various ways to use both the backwards-compatible API
and the new modular architecture features.
"""

from user_display import (
    UserStore,
    Config,
    MultiCriteriaFilter,
)
from user_display.formatters import get_formatter
from user_display.metrics import global_metrics
from user_display_optimized import display_users, get_user_by_id, filter_users


# Sample user data
sample_users = [
    {"id": 1, "name": "Alice Smith", "email": "alice@company.com", "role": "Admin", "status": "Active"},
    {"id": 2, "name": "Bob Jones", "email": "bob@company.com", "role": "User", "status": "Active"},
    {"id": 3, "name": "Charlie Brown", "email": "charlie@company.com", "role": "User", "status": "Inactive"},
    {"id": 4, "name": "Diana Prince", "email": "diana@company.com", "role": "Moderator", "status": "Active"},
    {"id": 5, "name": "Eve Wilson", "email": "eve@company.com", "role": "User", "status": "Active"},
]


def example_1_backwards_compatible():
    """Example 1: Using the backwards-compatible API."""
    print("=" * 80)
    print("Example 1: Backwards Compatible API")
    print("=" * 80)
    
    # Same API as original
    print("\n--- Display All Users ---")
    output = display_users(sample_users, show_all=True)
    print(output)
    
    print("\n--- Lookup by ID ---")
    user = get_user_by_id(sample_users, 3)
    print(f"Found: {user['name']} ({user['email']})")
    
    print("\n--- Filter Users ---")
    active_users = filter_users(sample_users, {"status": "Active"})
    print(f"Found {len(active_users)} active users")
    for user in active_users:
        print(f"  - {user['name']} ({user['role']})")


def example_2_different_formatters():
    """Example 2: Using different output formatters."""
    print("\n" + "=" * 80)
    print("Example 2: Different Formatters")
    print("=" * 80)
    
    # Compact format (default)
    print("\n--- Compact Format ---")
    formatter = get_formatter("compact")
    print(formatter.format_users(sample_users[:2], show_total=False))
    
    # Verbose format
    print("\n--- Verbose Format ---")
    formatter = get_formatter("verbose")
    print(formatter.format_users(sample_users[:2], show_total=False))
    
    # JSON-like format
    print("\n--- JSON-like Format ---")
    formatter = get_formatter("json_like")
    print(formatter.format_users(sample_users[:2], show_total=False))
    
    # Table format
    print("\n--- Table Format ---")
    formatter = get_formatter("table")
    print(formatter.format_users(sample_users[:3], show_total=False))


def example_3_field_selection():
    """Example 3: Selecting specific fields to display."""
    print("\n" + "=" * 80)
    print("Example 3: Field Selection")
    print("=" * 80)
    
    # Show only ID and name
    print("\n--- Only ID and Name ---")
    formatter = get_formatter("compact")
    print(formatter.format_users(sample_users, fields=["id", "name"]))
    
    # Show ID, name, and role
    print("\n--- ID, Name, and Role ---")
    print(formatter.format_users(sample_users, fields=["id", "name", "role"]))


def example_4_advanced_filtering():
    """Example 4: Advanced filtering with the new architecture."""
    print("\n" + "=" * 80)
    print("Example 4: Advanced Filtering")
    print("=" * 80)
    
    # Create a store
    store = UserStore(sample_users)
    
    # Filter with multiple criteria
    print("\n--- Filter: Active Users ---")
    criteria = {"status": "Active"}
    filter_obj = MultiCriteriaFilter(criteria)
    active = filter_obj.filter(store.get_all())
    print(f"Found {len(active)} active users")
    
    # Substring matching (case-insensitive by default)
    print("\n--- Filter: Users with 'smith' in name ---")
    criteria = {"name": "smith"}
    filter_obj = MultiCriteriaFilter(criteria)
    matches = filter_obj.filter(store.get_all())
    for user in matches:
        print(f"  - {user['name']}")
    
    # Multiple criteria (AND logic)
    print("\n--- Filter: Active Users (not Admin) ---")
    criteria = {"status": "Active", "role": "User"}
    filter_obj = MultiCriteriaFilter(criteria)
    matches = filter_obj.filter(store.get_all())
    print(f"Found {len(matches)} matching users")
    for user in matches:
        print(f"  - {user['name']} ({user['role']})")


def example_5_configuration():
    """Example 5: Using different configurations."""
    print("\n" + "=" * 80)
    print("Example 5: Configuration Profiles")
    print("=" * 80)
    
    # Default configuration
    print("\n--- Default Configuration ---")
    config = Config.default()
    store = UserStore(sample_users, config=config)
    print(f"Loaded {len(store)} users with default config")
    
    # High-performance configuration
    print("\n--- High-Performance Configuration ---")
    config = Config.high_performance()
    store = UserStore(sample_users, config=config)
    print(f"Loaded {len(store)} users with high-performance config")
    print(f"  - Caching: {config.enable_cache}")
    print(f"  - Metrics: {config.enable_metrics}")
    
    # Strict validation configuration
    print("\n--- Strict Validation Configuration ---")
    config = Config.strict()
    store = UserStore(sample_users, config=config)
    print(f"Loaded {len(store)} users with strict validation")
    print(f"  - Strict validation: {config.strict_validation}")
    print(f"  - Auto-fix malformed: {config.auto_fix_malformed}")


def example_6_metrics():
    """Example 6: Tracking performance metrics."""
    print("\n" + "=" * 80)
    print("Example 6: Performance Metrics")
    print("=" * 80)
    
    # Reset metrics
    global_metrics.reset()
    
    # Perform some operations
    store = UserStore(sample_users)
    _ = store.get_by_id(1)
    _ = store.get_by_id(2)
    _ = store.get_by_id(3)
    
    active = store.filter(lambda u: u["status"] == "Active")
    
    # Show metrics
    print("\n--- Metrics Summary ---")
    print(global_metrics.summary())
    
    print(f"\nTotal lookups: {global_metrics.get('store.lookups')}")
    print(f"Lookup hits: {global_metrics.get('store.lookup_hits')}")


def example_7_error_handling():
    """Example 7: Graceful error handling."""
    print("\n" + "=" * 80)
    print("Example 7: Error Handling")
    print("=" * 80)
    
    # Malformed data
    malformed_users = [
        {"id": 1, "name": "Valid User", "email": "valid@test.com", "role": "User", "status": "Active"},
        {"id": "bad_id", "name": "Invalid ID"},  # Missing fields, bad ID
        {"id": 3, "name": "Another Valid", "email": "valid2@test.com", "role": "User", "status": "Active"},
    ]
    
    print("\n--- Processing Malformed Data (Auto-Fix Mode) ---")
    config = Config(auto_fix_malformed=True, strict_validation=False, verbose_logging=False)
    store = UserStore(malformed_users, config=config)
    print(f"Successfully loaded {len(store)} users (from {len(malformed_users)} records)")
    
    # Show what we got
    for user in store.get_all():
        print(f"  - ID: {user['id']}, Name: {user['name']}, Email: {user.get('email', 'N/A')}")


def example_8_thread_safety():
    """Example 8: Thread-safe snapshot feature."""
    print("\n" + "=" * 80)
    print("Example 8: Thread-Safe Snapshots")
    print("=" * 80)
    
    # Create a store
    store = UserStore(sample_users)
    
    # Create snapshots (useful for concurrent access)
    print("\n--- Creating Snapshots ---")
    snapshot1 = store.snapshot()
    snapshot2 = store.snapshot()
    
    print(f"Original store: {len(store)} users")
    print(f"Snapshot 1: {len(snapshot1)} users")
    print(f"Snapshot 2: {len(snapshot2)} users")
    print("\nEach snapshot is an independent copy, safe for concurrent access")


if __name__ == "__main__":
    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 20 + "USER DISPLAY MODULE EXAMPLES" + " " * 30 + "║")
    print("╚" + "=" * 78 + "╝")
    
    # Run all examples
    example_1_backwards_compatible()
    example_2_different_formatters()
    example_3_field_selection()
    example_4_advanced_filtering()
    example_5_configuration()
    example_6_metrics()
    example_7_error_handling()
    example_8_thread_safety()
    
    print("\n" + "=" * 80)
    print("All examples completed successfully!")
    print("=" * 80)
