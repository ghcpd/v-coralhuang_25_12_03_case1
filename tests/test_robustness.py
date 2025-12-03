"""Robustness and error handling tests."""

import unittest
from user_display import (
    get_formatter,
    get_filter_strategy,
    get_store,
    MalformedUserError,
)


class TestRobustness(unittest.TestCase):
    """Test robustness and error handling."""

    def setUp(self):
        """Set up test data."""
        self.store = get_store()
        self.store.clear()

    def tearDown(self):
        """Clean up after tests."""
        self.store.clear()

    def test_missing_required_field(self):
        """Test handling of missing required fields."""
        malformed_user = {"id": 1, "name": "John"}  # Missing many required fields
        # Should log warnings but not crash
        try:
            self.store.add_user(malformed_user)
        except MalformedUserError:
            # Expected if validation is strict
            pass

    def test_formatter_with_missing_fields(self):
        """Test formatter handles missing fields gracefully."""
        users = [
            {"id": 1, "name": "John"},  # Missing fields
        ]
        formatter = get_formatter("compact")
        output = formatter.format_users(users)
        self.assertIn("N/A", output)  # Default value for missing fields

    def test_formatter_with_non_dict_user(self):
        """Test formatter rejects non-dict users."""
        users = ["not a dict"]
        formatter = get_formatter("compact")
        # Should not crash, should skip malformed
        output = formatter.format_users(users)
        self.assertTrue(isinstance(output, str))

    def test_filter_with_missing_field_in_criteria(self):
        """Test filtering when user lacks field in criteria."""
        users = [
            {"id": 1, "name": "John", "email": "john@test.com"},  # No role field
            {"id": 2, "name": "Jane", "email": "jane@test.com", "role": "User"},
        ]
        strategy = get_filter_strategy("simple")
        result = strategy.apply(users, {"role": "User"})
        # Should only match user with role field
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["id"], 2)

    def test_empty_user_list(self):
        """Test handling empty user list."""
        formatter = get_formatter("compact")
        output = formatter.format_users([])
        self.assertEqual(output, "")

    def test_empty_criteria(self):
        """Test filtering with empty criteria."""
        users = [
            {"id": 1, "name": "John", "email": "john@test.com", "role": "Admin", "status": "Active", "join_date": "2023-01-01", "last_login": "2025-12-01"},
            {"id": 2, "name": "Jane", "email": "jane@test.com", "role": "User", "status": "Active", "join_date": "2023-01-01", "last_login": "2025-12-01"},
        ]
        strategy = get_filter_strategy("simple")
        result = strategy.apply(users, {})
        self.assertEqual(len(result), 2)

    def test_unicode_characters(self):
        """Test handling of unicode characters in user data."""
        users = [
            {"id": 1, "name": "José García", "email": "jose@test.com", "role": "User", "status": "Active", "join_date": "2023-01-01", "last_login": "2025-12-01"},
            {"id": 2, "name": "李明", "email": "li@test.com", "role": "User", "status": "Active", "join_date": "2023-01-01", "last_login": "2025-12-01"},
        ]
        formatter = get_formatter("compact")
        output = formatter.format_users(users)
        self.assertIn("José", output)
        self.assertIn("李明", output)

    def test_special_characters_in_fields(self):
        """Test handling special characters in user fields."""
        users = [
            {"id": 1, "name": "O'Brien | Special", "email": "user+test@example.com", "role": "User", "status": "Active", "join_date": "2023-01-01", "last_login": "2025-12-01"},
        ]
        formatter = get_formatter("compact")
        output = formatter.format_users(users)
        self.assertIn("O'Brien", output)
        self.assertIn("+test", output)


class TestMetrics(unittest.TestCase):
    """Test metrics tracking."""

    def setUp(self):
        """Set up test data."""
        from user_display import get_metrics
        self.metrics = get_metrics()
        self.metrics.reset()

    def test_metrics_initialization(self):
        """Test metrics are initialized correctly."""
        summary = self.metrics.get_summary()
        self.assertIn("counters", summary)
        self.assertIn("display_operations", summary["counters"])
        self.assertEqual(summary["counters"]["display_operations"], 0)

    def test_metrics_increments(self):
        """Test metrics can be incremented."""
        self.metrics.increment("display_operations", 5)
        self.assertEqual(self.metrics.get_counter("display_operations"), 5)

    def test_metrics_reset(self):
        """Test metrics can be reset."""
        self.metrics.increment("display_operations", 10)
        self.metrics.reset()
        self.assertEqual(self.metrics.get_counter("display_operations"), 0)


if __name__ == "__main__":
    unittest.main()
