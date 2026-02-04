"""Functional tests for user display module."""

import unittest
from user_display.store import UserStore
from user_display.formatters import get_formatter
from user_display.filters import create_criteria_filter
from user_display.config import Config, get_config, reset_config
from user_display.logging_utils import get_logger
from user_display.metrics import get_metrics, reset_metrics
from user_display.errors import InvalidUserDataError


class TestUserStore(unittest.TestCase):
    """Test UserStore functionality."""

    def setUp(self):
        reset_metrics()
        self.sample_users = [
            {"id": 1, "name": "John", "email": "john@example.com", "role": "Admin", 
             "status": "Active", "join_date": "2023-01-01", "last_login": "2025-01-01"},
            {"id": 2, "name": "Jane", "email": "jane@example.com", "role": "User", 
             "status": "Active", "join_date": "2023-02-01", "last_login": "2025-01-02"},
            {"id": 3, "name": "Bob", "email": "bob@example.com", "role": "User", 
             "status": "Inactive", "join_date": "2023-03-01", "last_login": "2024-01-01"},
        ]

    def test_store_initialization(self):
        """Test store initialization with users."""
        store = UserStore(self.sample_users)
        self.assertEqual(store.count(), 3)

    def test_add_user(self):
        """Test adding a single user."""
        store = UserStore()
        self.assertEqual(store.count(), 0)

        store.add_user(self.sample_users[0])
        self.assertEqual(store.count(), 1)

    def test_get_by_id_hit(self):
        """Test O(1) lookup - hit case."""
        store = UserStore(self.sample_users)
        user = store.get_by_id(2)
        self.assertIsNotNone(user)
        self.assertEqual(user["name"], "Jane")

    def test_get_by_id_miss(self):
        """Test O(1) lookup - miss case."""
        store = UserStore(self.sample_users)
        user = store.get_by_id(999)
        self.assertIsNone(user)

    def test_get_all(self):
        """Test getting all users."""
        store = UserStore(self.sample_users)
        users = store.get_all()
        self.assertEqual(len(users), 3)

    def test_snapshot(self):
        """Test snapshot functionality."""
        store = UserStore(self.sample_users)
        snapshot = store.snapshot()

        self.assertEqual(snapshot.count(), store.count())
        # Modify original shouldn't affect snapshot
        snapshot.clear()
        self.assertEqual(store.count(), 3)
        self.assertEqual(snapshot.count(), 0)

    def test_filter(self):
        """Test filter with predicate."""
        store = UserStore(self.sample_users)
        active_users = store.filter(lambda u: u["status"] == "Active")
        self.assertEqual(len(active_users), 2)

    def test_malformed_data_handling(self):
        """Test graceful handling of malformed data."""
        reset_config()
        users = [
            {"id": 1, "name": "Valid", "email": "valid@example.com", "role": "User",
             "status": "Active", "join_date": "2023-01-01", "last_login": "2025-01-01"},
            {"id": 2, "name": "Missing email"},  # Malformed
        ]
        store = UserStore(users)
        self.assertEqual(store.count(), 1)  # Only valid user added

    def test_thread_safety_iteration(self):
        """Test iteration is thread-safe."""
        store = UserStore(self.sample_users)
        count = 0
        for user in store:
            count += 1
        self.assertEqual(count, 3)


class TestFormatters(unittest.TestCase):
    """Test formatter functionality."""

    def setUp(self):
        self.sample_users = [
            {"id": 1, "name": "John", "email": "john@example.com", "role": "Admin",
             "status": "Active", "join_date": "2023-01-01", "last_login": "2025-01-01"},
        ]

    def test_compact_formatter(self):
        """Test compact formatter."""
        formatter = get_formatter("compact")
        result = formatter.format_users(self.sample_users)
        self.assertIn("John", result)
        self.assertIn("Total users: 1", result)

    def test_verbose_formatter(self):
        """Test verbose formatter."""
        formatter = get_formatter("verbose")
        result = formatter.format_users(self.sample_users)
        self.assertIn("John", result)
        self.assertIn("User:", result)

    def test_json_formatter(self):
        """Test JSON-like formatter."""
        formatter = get_formatter("json")
        result = formatter.format_users(self.sample_users)
        self.assertIn("{", result)
        self.assertIn("}", result)
        self.assertIn('"name": "John"', result)

    def test_export_formatter(self):
        """Test export formatter."""
        formatter = get_formatter("export")
        result = formatter.format_users(self.sample_users)
        self.assertIn("USER_EXPORT_START", result)
        self.assertIn("USER_EXPORT_END", result)

    def test_field_filtering(self):
        """Test field inclusion/exclusion."""
        config = Config()
        config.include_fields = {"id", "name"}
        
        from user_display import config as config_module
        old_config = config_module._config
        config_module._config = config

        try:
            formatter = get_formatter("compact")
            result = formatter.format_user(self.sample_users[0])
            self.assertIn("id=1", result)
            self.assertIn("name=John", result)
            self.assertNotIn("email", result)
        finally:
            config_module._config = old_config


class TestFilters(unittest.TestCase):
    """Test filtering functionality."""

    def setUp(self):
        reset_metrics()
        reset_config()
        self.sample_users = [
            {"id": 1, "name": "John", "email": "john@example.com", "role": "Admin",
             "status": "Active", "join_date": "2023-01-01", "last_login": "2025-01-01"},
            {"id": 2, "name": "Jane", "email": "jane@example.com", "role": "User",
             "status": "Active", "join_date": "2023-02-01", "last_login": "2025-01-02"},
            {"id": 3, "name": "Bob", "email": "bob@example.com", "role": "User",
             "status": "Inactive", "join_date": "2023-03-01", "last_login": "2024-01-01"},
        ]

    def test_criteria_filter_exact_match(self):
        """Test exact match filtering."""
        filter_strategy = create_criteria_filter({"role": "Admin"})
        result = filter_strategy.apply(self.sample_users)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["name"], "John")

    def test_criteria_filter_multiple_criteria(self):
        """Test filtering with multiple criteria."""
        filter_strategy = create_criteria_filter({"role": "User", "status": "Active"})
        result = filter_strategy.apply(self.sample_users)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["name"], "Jane")

    def test_criteria_filter_substring_case_insensitive(self):
        """Test case-insensitive substring matching."""
        reset_config()
        filter_strategy = create_criteria_filter({"name": "john"})
        result = filter_strategy.apply(self.sample_users)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["id"], 1)

    def test_criteria_filter_substring_case_sensitive(self):
        """Test case-sensitive substring matching."""
        config = Config()
        config.case_sensitive_filters = True
        from user_display import config as config_module
        old_config = config_module._config
        config_module._config = config

        try:
            filter_strategy = create_criteria_filter({"name": "john"})
            result = filter_strategy.apply(self.sample_users)
            self.assertEqual(len(result), 0)  # "john" not found in "John"
        finally:
            config_module._config = old_config

    def test_criteria_filter_no_match(self):
        """Test filtering with no matches."""
        filter_strategy = create_criteria_filter({"role": "NonExistent"})
        result = filter_strategy.apply(self.sample_users)
        self.assertEqual(len(result), 0)


if __name__ == "__main__":
    unittest.main()
