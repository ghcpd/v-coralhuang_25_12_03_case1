"""Functional tests for the user display module."""

import unittest
from user_display import (
    UserStore,
    Config,
    CompactFormatter,
    VerboseFormatter,
    JSONLikeFormatter,
    MultiCriteriaFilter,
    ValidationError,
)
from user_display.formatters import TableFormatter, get_formatter
from user_display.filters import (
    FieldMatchFilter,
    SubstringMatchFilter,
    CompositeFilter,
)


class TestUserStore(unittest.TestCase):
    """Test UserStore functionality."""

    def setUp(self):
        """Set up test data."""
        self.users = [
            {"id": 1, "name": "Alice", "email": "alice@test.com", "role": "Admin", "status": "Active"},
            {"id": 2, "name": "Bob", "email": "bob@test.com", "role": "User", "status": "Active"},
            {"id": 3, "name": "Charlie", "email": "charlie@test.com", "role": "User", "status": "Inactive"},
        ]

    def test_store_initialization(self):
        """Test store can be initialized with users."""
        store = UserStore(self.users)
        self.assertEqual(len(store), 3)

    def test_o1_lookup(self):
        """Test O(1) ID lookup."""
        store = UserStore(self.users)
        user = store.get_by_id(2)
        self.assertIsNotNone(user)
        self.assertEqual(user["name"], "Bob")

    def test_lookup_missing_user(self):
        """Test lookup returns None for missing user."""
        store = UserStore(self.users)
        user = store.get_by_id(999)
        self.assertIsNone(user)

    def test_get_all(self):
        """Test get_all returns all users."""
        store = UserStore(self.users)
        all_users = store.get_all()
        self.assertEqual(len(all_users), 3)

    def test_filter_with_predicate(self):
        """Test filtering with predicate."""
        store = UserStore(self.users)
        active_users = store.filter(lambda u: u["status"] == "Active")
        self.assertEqual(len(active_users), 2)

    def test_snapshot(self):
        """Test snapshot creates independent copy."""
        store = UserStore(self.users)
        snapshot = store.snapshot()
        
        self.assertEqual(len(snapshot), len(store))
        # Verify they're independent
        self.assertIsNot(store, snapshot)


class TestValidation(unittest.TestCase):
    """Test validation and error handling."""

    def test_validation_with_missing_fields(self):
        """Test handling of records with missing fields."""
        users = [
            {"id": 1, "name": "Alice"},  # Missing required fields
        ]
        config = Config(auto_fix_malformed=True, strict_validation=False)
        store = UserStore(users, config=config)
        
        # Should auto-fix
        user = store.get_by_id(1)
        self.assertIsNotNone(user)
        self.assertEqual(user["email"], "UNKNOWN")

    def test_strict_validation_raises_error(self):
        """Test strict validation raises error."""
        users = [
            {"id": 1, "name": "Alice"},  # Missing required fields
        ]
        config = Config(auto_fix_malformed=False, strict_validation=True)
        
        with self.assertRaises(ValidationError):
            store = UserStore(users, config=config)

    def test_invalid_id_handling(self):
        """Test handling of invalid IDs."""
        users = [
            {"id": "not_a_number", "name": "Alice", "email": "alice@test.com", 
             "role": "User", "status": "Active"},
        ]
        config = Config(auto_fix_malformed=True, strict_validation=False)
        store = UserStore(users, config=config)
        
        # Should auto-fix with index
        self.assertEqual(len(store), 1)


class TestFormatters(unittest.TestCase):
    """Test formatter functionality."""

    def setUp(self):
        """Set up test data."""
        self.users = [
            {"id": 1, "name": "Alice", "email": "alice@test.com", "role": "Admin"},
            {"id": 2, "name": "Bob", "email": "bob@test.com", "role": "User"},
        ]

    def test_compact_formatter(self):
        """Test compact formatter output."""
        formatter = CompactFormatter()
        output = formatter.format_users(self.users, show_total=False)
        
        self.assertIn("Alice", output)
        self.assertIn("Bob", output)
        self.assertIn("alice@test.com", output)

    def test_verbose_formatter(self):
        """Test verbose formatter output."""
        formatter = VerboseFormatter()
        output = formatter.format_users(self.users, show_total=False)
        
        self.assertIn("User ID: 1", output)
        self.assertIn("Name: Alice", output)

    def test_json_like_formatter(self):
        """Test JSON-like formatter output."""
        formatter = JSONLikeFormatter()
        output = formatter.format_users(self.users, show_total=False)
        
        self.assertIn("{", output)
        self.assertIn("}", output)
        self.assertIn('"id": 1', output)

    def test_table_formatter(self):
        """Test table formatter output."""
        formatter = TableFormatter()
        output = formatter.format_users(self.users, show_total=False)
        
        self.assertIn("|", output)
        self.assertIn("Alice", output)
        self.assertIn("Bob", output)

    def test_field_selection(self):
        """Test formatting with field selection."""
        formatter = CompactFormatter()
        output = formatter.format_users(self.users, show_total=False, fields=["id", "name"])
        
        self.assertIn("Alice", output)
        self.assertNotIn("alice@test.com", output)

    def test_get_formatter_factory(self):
        """Test formatter factory function."""
        formatter = get_formatter("compact")
        self.assertIsInstance(formatter, CompactFormatter)
        
        formatter = get_formatter("verbose")
        self.assertIsInstance(formatter, VerboseFormatter)
        
        formatter = get_formatter("json_like")
        self.assertIsInstance(formatter, JSONLikeFormatter)


class TestFilters(unittest.TestCase):
    """Test filter strategies."""

    def setUp(self):
        """Set up test data."""
        self.users = [
            {"id": 1, "name": "Alice Smith", "email": "alice@test.com", "role": "Admin", "status": "Active"},
            {"id": 2, "name": "Bob Jones", "email": "bob@test.com", "role": "User", "status": "Active"},
            {"id": 3, "name": "Charlie Brown", "email": "charlie@test.com", "role": "User", "status": "Inactive"},
        ]

    def test_field_match_filter(self):
        """Test exact field matching."""
        filter_obj = FieldMatchFilter("role", "Admin")
        
        matches = [u for u in self.users if filter_obj.matches(u)]
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0]["name"], "Alice Smith")

    def test_substring_match_filter(self):
        """Test substring matching."""
        filter_obj = SubstringMatchFilter("name", "Smith")
        
        matches = [u for u in self.users if filter_obj.matches(u)]
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0]["name"], "Alice Smith")

    def test_case_insensitive_filtering(self):
        """Test case-insensitive filtering."""
        config = Config(case_sensitive=False)
        filter_obj = SubstringMatchFilter("name", "alice", config=config)
        
        matches = [u for u in self.users if filter_obj.matches(u)]
        self.assertEqual(len(matches), 1)

    def test_case_sensitive_filtering(self):
        """Test case-sensitive filtering."""
        config = Config(case_sensitive=True)
        filter_obj = SubstringMatchFilter("name", "alice", config=config)
        
        matches = [u for u in self.users if filter_obj.matches(u)]
        self.assertEqual(len(matches), 0)  # Won't match "Alice"

    def test_composite_filter_and(self):
        """Test composite filter with AND logic."""
        filter1 = FieldMatchFilter("role", "User")
        filter2 = FieldMatchFilter("status", "Active")
        composite = CompositeFilter([filter1, filter2], mode="AND")
        
        matches = [u for u in self.users if composite.matches(u)]
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0]["name"], "Bob Jones")

    def test_composite_filter_or(self):
        """Test composite filter with OR logic."""
        filter1 = FieldMatchFilter("role", "Admin")
        filter2 = FieldMatchFilter("status", "Inactive")
        composite = CompositeFilter([filter1, filter2], mode="OR")
        
        matches = [u for u in self.users if composite.matches(u)]
        self.assertEqual(len(matches), 2)

    def test_multi_criteria_filter(self):
        """Test multi-criteria filter."""
        criteria = {"role": "User", "status": "Active"}
        filter_obj = MultiCriteriaFilter(criteria)
        
        result = filter_obj.filter(self.users)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["name"], "Bob Jones")

    def test_multi_criteria_substring_match(self):
        """Test multi-criteria with substring matching."""
        criteria = {"name": "Brown", "status": "Inactive"}
        filter_obj = MultiCriteriaFilter(criteria)
        
        result = filter_obj.filter(self.users)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["name"], "Charlie Brown")


class TestBackwardsCompatibility(unittest.TestCase):
    """Test backwards compatibility with original API."""

    def setUp(self):
        """Set up test data."""
        self.users = [
            {"id": 1, "name": "Alice", "email": "alice@test.com", "role": "Admin", 
             "status": "Active", "join_date": "2023-01-01", "last_login": "2025-12-01"},
            {"id": 2, "name": "Bob", "email": "bob@test.com", "role": "User", 
             "status": "Active", "join_date": "2023-06-01", "last_login": "2025-12-02"},
        ]

    def test_display_users(self):
        """Test display_users function."""
        from user_display_optimized import display_users
        
        output = display_users(self.users, show_all=True)
        self.assertIn("Alice", output)
        self.assertIn("Bob", output)
        self.assertIn("Total users", output)

    def test_get_user_by_id(self):
        """Test get_user_by_id function."""
        from user_display_optimized import get_user_by_id
        
        user = get_user_by_id(self.users, 1)
        self.assertIsNotNone(user)
        self.assertEqual(user["name"], "Alice")
        
        missing = get_user_by_id(self.users, 999)
        self.assertIsNone(missing)

    def test_filter_users(self):
        """Test filter_users function."""
        from user_display_optimized import filter_users
        
        filtered = filter_users(self.users, {"role": "Admin"})
        self.assertEqual(len(filtered), 1)
        self.assertEqual(filtered[0]["name"], "Alice")

    def test_export_users_to_string(self):
        """Test export_users_to_string function."""
        from user_display_optimized import export_users_to_string
        
        output = export_users_to_string(self.users)
        self.assertIn("USER_EXPORT_START", output)
        self.assertIn("USER_EXPORT_END", output)
        self.assertIn("Alice", output)


if __name__ == "__main__":
    unittest.main()
