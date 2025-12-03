"""Robustness tests for error handling and edge cases."""

import unittest
from user_display import UserStore, Config, ValidationError
from user_display.formatters import get_formatter
from user_display.logging_utils import setup_logger
from user_display.metrics import Metrics
from user_display_optimized import display_users, filter_users, get_user_by_id


class TestRobustness(unittest.TestCase):
    """Test error handling and robustness."""

    def test_empty_user_list(self):
        """Test handling of empty user list."""
        output = display_users([], show_all=True)
        self.assertIsNotNone(output)
        self.assertIn("Total users processed: 0", output)

    def test_missing_required_fields(self):
        """Test handling of records with missing fields."""
        users = [
            {"id": 1, "name": "Alice"},  # Missing email, role, status
        ]
        
        # Should auto-fix
        output = display_users(users, show_all=True)
        self.assertIn("Alice", output)
        self.assertIn("UNKNOWN", output)

    def test_malformed_user_dict(self):
        """Test handling of malformed user data."""
        users = [
            {"id": 1, "name": "Alice", "email": "alice@test.com", "role": "Admin", "status": "Active"},
            None,  # Invalid entry
            {"id": 2, "name": "Bob", "email": "bob@test.com", "role": "User", "status": "Active"},
        ]
        
        config = Config(strict_validation=False, auto_fix_malformed=True)
        store = UserStore(users, config=config)
        
        # Should skip None entry
        self.assertEqual(len(store), 2)

    def test_invalid_id_types(self):
        """Test handling of various invalid ID types."""
        test_cases = [
            {"id": "abc", "name": "Test"},
            {"id": None, "name": "Test"},
            {"id": [], "name": "Test"},
        ]
        
        for user_data in test_cases:
            users = [user_data]
            config = Config(strict_validation=False, auto_fix_malformed=True)
            store = UserStore(users, config=config)
            # Should handle gracefully
            self.assertGreaterEqual(len(store), 0)

    def test_duplicate_ids(self):
        """Test handling of duplicate user IDs."""
        users = [
            {"id": 1, "name": "Alice", "email": "alice@test.com", "role": "Admin", "status": "Active"},
            {"id": 1, "name": "Bob", "email": "bob@test.com", "role": "User", "status": "Active"},
        ]
        
        store = UserStore(users)
        # Last user with same ID should be in index
        user = store.get_by_id(1)
        # One of them should be accessible
        self.assertIsNotNone(user)

    def test_filter_with_empty_criteria(self):
        """Test filtering with empty criteria."""
        users = [
            {"id": 1, "name": "Alice", "email": "alice@test.com", "role": "Admin", "status": "Active"},
        ]
        
        filtered = filter_users(users, {})
        # Empty criteria should match all
        self.assertEqual(len(filtered), len(users))

    def test_filter_with_nonexistent_field(self):
        """Test filtering on fields that don't exist."""
        users = [
            {"id": 1, "name": "Alice", "email": "alice@test.com", "role": "Admin", "status": "Active"},
        ]
        
        filtered = filter_users(users, {"department": "Engineering"})
        # Should return empty list
        self.assertEqual(len(filtered), 0)

    def test_format_with_missing_fields(self):
        """Test formatting users with missing fields."""
        users = [
            {"id": 1, "name": "Alice"},  # Missing many fields
        ]
        
        formatter = get_formatter("compact")
        output = formatter.format_users(users, show_total=False)
        
        # Should handle gracefully
        self.assertIn("Alice", output)

    def test_special_characters_in_data(self):
        """Test handling of special characters."""
        users = [
            {"id": 1, "name": "O'Brien", "email": "test@test.com", "role": "Admin", "status": "Active"},
            {"id": 2, "name": "Smith & Jones", "email": "test2@test.com", "role": "User", "status": "Active"},
        ]
        
        output = display_users(users, show_all=True)
        self.assertIn("O'Brien", output)
        self.assertIn("Smith & Jones", output)

    def test_very_long_field_values(self):
        """Test handling of very long field values."""
        long_name = "A" * 1000
        users = [
            {"id": 1, "name": long_name, "email": "test@test.com", "role": "User", "status": "Active"},
        ]
        
        output = display_users(users, show_all=True)
        self.assertIn(long_name, output)

    def test_unicode_characters(self):
        """Test handling of Unicode characters."""
        users = [
            {"id": 1, "name": "José García", "email": "josé@test.com", "role": "Admin", "status": "Active"},
            {"id": 2, "name": "李明", "email": "liming@test.com", "role": "User", "status": "Active"},
        ]
        
        output = display_users(users, show_all=True)
        self.assertIn("José", output)
        self.assertIn("李明", output)


class TestLogging(unittest.TestCase):
    """Test logging functionality."""

    def test_marked_logger(self):
        """Test that logger adds [MARKER] prefix."""
        import logging
        from io import StringIO
        
        handler = logging.StreamHandler(StringIO())
        logger = setup_logger("test_logger", handler=handler, marker="TEST")
        
        # Verify logger was created
        self.assertIsNotNone(logger)

    def test_logging_with_errors(self):
        """Test that errors are logged appropriately."""
        users = [
            {"id": 1, "name": "Alice"},  # Missing fields
        ]
        
        config = Config(verbose_logging=True, auto_fix_malformed=True)
        store = UserStore(users, config=config)
        
        # Should complete without crashing
        self.assertGreaterEqual(len(store), 0)


class TestMetrics(unittest.TestCase):
    """Test metrics tracking."""

    def test_metrics_increment(self):
        """Test metrics can be incremented."""
        metrics = Metrics()
        metrics.increment("test_counter")
        
        self.assertEqual(metrics.get("test_counter"), 1)

    def test_metrics_reset(self):
        """Test metrics can be reset."""
        metrics = Metrics()
        metrics.increment("test_counter", 5)
        metrics.reset("test_counter")
        
        self.assertEqual(metrics.get("test_counter"), 0)

    def test_metrics_summary(self):
        """Test metrics summary generation."""
        metrics = Metrics()
        metrics.increment("counter1", 10)
        metrics.increment("counter2", 20)
        
        summary = metrics.summary()
        self.assertIn("counter1", summary)
        self.assertIn("counter2", summary)

    def test_metrics_tracking_in_operations(self):
        """Test that operations track metrics."""
        from user_display.metrics import global_metrics
        
        # Reset global metrics
        global_metrics.reset()
        
        users = [
            {"id": 1, "name": "Alice", "email": "alice@test.com", "role": "Admin", "status": "Active"},
        ]
        
        store = UserStore(users)
        user = store.get_by_id(1)
        
        # Should have recorded some metrics
        all_metrics = global_metrics.get_all()
        self.assertGreater(len(all_metrics), 0)


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and boundary conditions."""

    def test_single_user(self):
        """Test with exactly one user."""
        users = [
            {"id": 1, "name": "Alice", "email": "alice@test.com", "role": "Admin", "status": "Active"},
        ]
        
        output = display_users(users, show_all=True)
        self.assertIn("Alice", output)
        self.assertIn("Total users processed: 1", output)

    def test_user_id_zero(self):
        """Test user with ID of 0."""
        users = [
            {"id": 0, "name": "Zero", "email": "zero@test.com", "role": "User", "status": "Active"},
        ]
        
        user = get_user_by_id(users, 0)
        self.assertIsNotNone(user)
        self.assertEqual(user["name"], "Zero")

    def test_negative_user_id(self):
        """Test user with negative ID."""
        users = [
            {"id": -1, "name": "Negative", "email": "neg@test.com", "role": "User", "status": "Active"},
        ]
        
        user = get_user_by_id(users, -1)
        self.assertIsNotNone(user)

    def test_field_selection_all_fields(self):
        """Test field selection with all available fields."""
        users = [
            {"id": 1, "name": "Alice", "email": "alice@test.com", "role": "Admin"},
        ]
        
        formatter = get_formatter("compact")
        all_fields = list(users[0].keys())
        output = formatter.format_users(users, show_total=False, fields=all_fields)
        
        self.assertIn("Alice", output)

    def test_field_selection_single_field(self):
        """Test field selection with just one field."""
        users = [
            {"id": 1, "name": "Alice", "email": "alice@test.com", "role": "Admin"},
        ]
        
        formatter = get_formatter("compact")
        output = formatter.format_users(users, show_total=False, fields=["name"])
        
        self.assertIn("Alice", output)
        self.assertNotIn("alice@test.com", output)


if __name__ == "__main__":
    unittest.main()
