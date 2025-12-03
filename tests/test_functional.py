"""Functional tests for the user_display module."""

import unittest
from user_display import (
    get_store,
    get_formatter,
    get_filter_strategy,
    FilterCache,
    Config,
)


class TestFormatters(unittest.TestCase):
    """Test formatting functions."""

    def setUp(self):
        """Set up test data."""
        self.users = [
            {"id": 1, "name": "John", "email": "john@test.com", "role": "Admin", "status": "Active", "join_date": "2023-01-01", "last_login": "2025-12-01"},
            {"id": 2, "name": "Jane", "email": "jane@test.com", "role": "User", "status": "Inactive", "join_date": "2023-06-01", "last_login": "2025-11-01"},
        ]

    def test_compact_formatter(self):
        """Test compact formatter."""
        formatter = get_formatter("compact")
        output = formatter.format_users(self.users)
        self.assertIn("John", output)
        self.assertIn("jane@test.com", output)
        self.assertIn("Admin", output)

    def test_verbose_formatter(self):
        """Test verbose formatter."""
        formatter = get_formatter("verbose")
        output = formatter.format_users(self.users)
        self.assertIn("User ID: 1", output)
        self.assertIn("Name: John", output)
        self.assertIn("Role: Admin", output)

    def test_json_formatter(self):
        """Test JSON formatter."""
        formatter = get_formatter("json")
        output = formatter.format_users(self.users)
        self.assertIn('"id": 1', output)
        self.assertIn('"name": "John"', output)

    def test_export_formatter(self):
        """Test export formatter."""
        formatter = get_formatter("export")
        output = formatter.format_users(self.users)
        self.assertIn("USER_EXPORT_START", output)
        self.assertIn("USER_EXPORT_END", output)
        self.assertIn("User ID: 1", output)

    def test_formatter_with_malformed_user(self):
        """Test formatter handles malformed users gracefully."""
        users = [
            {"id": 1, "name": "John", "email": "john@test.com", "role": "Admin", "status": "Active", "join_date": "2023-01-01", "last_login": "2025-12-01"},
            {"id": 2},  # Missing required fields
            {"id": 3, "name": "Jane", "email": "jane@test.com", "role": "User", "status": "Active", "join_date": "2023-06-01", "last_login": "2025-11-01"},
        ]
        formatter = get_formatter("compact")
        # Should not raise an exception
        output = formatter.format_users(users)
        self.assertIn("John", output)
        self.assertIn("Jane", output)


class TestFilters(unittest.TestCase):
    """Test filtering functions."""

    def setUp(self):
        """Set up test data."""
        self.users = [
            {"id": 1, "name": "John Doe", "email": "john@test.com", "role": "Admin", "status": "Active", "join_date": "2023-01-01", "last_login": "2025-12-01"},
            {"id": 2, "name": "Jane Smith", "email": "jane@test.com", "role": "User", "status": "Inactive", "join_date": "2023-06-01", "last_login": "2025-11-01"},
            {"id": 3, "name": "Bob Johnson", "email": "bob@test.com", "role": "User", "status": "Active", "join_date": "2023-03-01", "last_login": "2025-11-15"},
        ]

    def test_filter_by_role(self):
        """Test filtering by role."""
        strategy = get_filter_strategy("simple")
        result = strategy.apply(self.users, {"role": "User"})
        self.assertEqual(len(result), 2)
        self.assertTrue(all(u["role"] == "User" for u in result))

    def test_filter_by_status(self):
        """Test filtering by status."""
        strategy = get_filter_strategy("simple")
        result = strategy.apply(self.users, {"status": "Active"})
        self.assertEqual(len(result), 2)

    def test_filter_by_name_substring(self):
        """Test filtering by name substring."""
        strategy = get_filter_strategy("simple")
        result = strategy.apply(self.users, {"name": "John"})
        self.assertEqual(len(result), 2)  # "John Doe" and "Bob Johnson"

    def test_filter_multiple_criteria(self):
        """Test filtering with multiple criteria."""
        strategy = get_filter_strategy("simple")
        result = strategy.apply(self.users, {"role": "User", "status": "Active"})
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["id"], 3)

    def test_filter_case_insensitive(self):
        """Test case-insensitive filtering."""
        Config.CASE_SENSITIVE_FILTERS = False
        strategy = get_filter_strategy("simple")
        result = strategy.apply(self.users, {"role": "admin"})
        self.assertEqual(len(result), 1)
        Config.CASE_SENSITIVE_FILTERS = False  # Reset to default

    def test_filter_cache(self):
        """Test filter cache."""
        cache = FilterCache(max_entries=5)
        user_ids = [1, 2, 3]
        criteria = {"role": "User"}

        # First access should miss
        result = cache.get(user_ids, criteria)
        self.assertIsNone(result)
        self.assertEqual(cache.miss_count, 1)

        # Store result
        filtered = [self.users[1], self.users[2]]
        cache.set(user_ids, criteria, filtered)

        # Second access should hit
        result = cache.get(user_ids, criteria)
        self.assertIsNotNone(result)
        self.assertEqual(cache.hit_count, 1)


class TestUserStore(unittest.TestCase):
    """Test UserStore functionality."""

    def setUp(self):
        """Set up test data."""
        self.store = get_store()
        self.store.clear()

    def tearDown(self):
        """Clean up after tests."""
        self.store.clear()

    def test_add_and_retrieve_user(self):
        """Test adding and retrieving a user."""
        user = {"id": 1, "name": "John", "email": "john@test.com", "role": "Admin", "status": "Active", "join_date": "2023-01-01", "last_login": "2025-12-01"}
        self.store.add_user(user)
        retrieved = self.store.get_user_by_id(1)
        self.assertIsNotNone(retrieved, "User should be retrieved from store")
        if retrieved:
            self.assertEqual(retrieved["name"], "John")

    def test_user_id_lookup_efficiency(self):
        """Test O(1) user ID lookup."""
        # Add multiple users
        for i in range(100):
            user = {"id": i, "name": f"User{i}", "email": f"user{i}@test.com", "role": "User", "status": "Active", "join_date": "2023-01-01", "last_login": "2025-12-01"}
            self.store.add_user(user)

        # Lookup should be O(1) and fast
        result = self.store.get_user_by_id(99)
        self.assertIsNotNone(result, "User 99 should be found in store")
        if result:
            self.assertEqual(result["name"], "User99")

    def test_get_all_users(self):
        """Test retrieving all users."""
        users = [
            {"id": i, "name": f"User{i}", "email": f"user{i}@test.com", "role": "User", "status": "Active", "join_date": "2023-01-01", "last_login": "2025-12-01"}
            for i in range(5)
        ]
        self.store.add_users(users)
        all_users = self.store.get_all_users()
        self.assertEqual(len(all_users), 5)

    def test_remove_user(self):
        """Test removing a user."""
        user = {"id": 1, "name": "John", "email": "john@test.com", "role": "Admin", "status": "Active", "join_date": "2023-01-01", "last_login": "2025-12-01"}
        self.store.add_user(user)
        removed = self.store.remove_user(1)
        self.assertTrue(removed)
        result = self.store.get_user_by_id(1)
        self.assertIsNone(result)

    def test_snapshot(self):
        """Test creating a snapshot."""
        user = {"id": 1, "name": "John", "email": "john@test.com", "role": "Admin", "status": "Active", "join_date": "2023-01-01", "last_login": "2025-12-01"}
        self.store.add_user(user)
        snapshot = self.store.snapshot()
        self.assertEqual(len(snapshot), 1)
        self.assertEqual(snapshot[0]["name"], "John")


if __name__ == "__main__":
    unittest.main()
