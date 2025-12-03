"""Robustness tests for error handling and edge cases."""

import unittest
from user_display.store import UserStore
from user_display.errors import InvalidUserDataError
from user_display.config import Config, reset_config
from user_display.metrics import get_metrics, reset_metrics


class TestRobustness(unittest.TestCase):
    """Test robustness and error handling."""

    def setUp(self):
        reset_metrics()
        reset_config()

    def test_empty_store(self):
        """Test operations on empty store."""
        store = UserStore()
        self.assertEqual(store.count(), 0)
        self.assertEqual(len(store.get_all()), 0)
        self.assertIsNone(store.get_by_id(1))

    def test_missing_fields(self):
        """Test handling of missing required fields."""
        incomplete_user = {"id": 1, "name": "John"}  # Missing required fields

        store = UserStore([incomplete_user])
        # Should skip malformed record (default behavior)
        self.assertEqual(store.count(), 0)

    def test_invalid_field_types(self):
        """Test handling of invalid field types."""
        invalid_user = {
            "id": 1,
            "name": "John",
            "email": "john@example.com",
            "role": "Admin",
            "status": "Active",
            "join_date": ["2023-01-01"],  # Should be string
            "last_login": "2025-01-01",
        }

        store = UserStore([invalid_user])
        # Should skip due to invalid type
        self.assertEqual(store.count(), 0)

    def test_strict_validation_mode(self):
        """Test strict validation mode raises exception."""
        config = Config()
        config.skip_malformed_records = False
        config.validate_on_insert = True

        from user_display import config as config_module
        old_config = config_module._config
        config_module._config = config

        try:
            incomplete_user = {"id": 1, "name": "John"}
            with self.assertRaises(InvalidUserDataError):
                UserStore([incomplete_user])
        finally:
            config_module._config = old_config

    def test_duplicate_user_update(self):
        """Test updating existing user."""
        store = UserStore()
        user1 = {
            "id": 1, "name": "John", "email": "john@example.com", "role": "Admin",
            "status": "Active", "join_date": "2023-01-01", "last_login": "2025-01-01"
        }
        store.add_user(user1)

        user1_updated = dict(user1)
        user1_updated["name"] = "Jane"
        store.add_user(user1_updated)

        self.assertEqual(store.count(), 1)
        retrieved = store.get_by_id(1)
        self.assertEqual(retrieved["name"], "Jane")

    def test_filter_with_error(self):
        """Test filter handles errors gracefully."""
        users = [
            {"id": 1, "name": "John", "email": "john@example.com", "role": "Admin",
             "status": "Active", "join_date": "2023-01-01", "last_login": "2025-01-01"},
        ]

        store = UserStore(users)

        def bad_predicate(user):
            if user["id"] == 1:
                raise ValueError("Test error")
            return True

        result = store.filter(bad_predicate)
        # Should handle error and continue
        self.assertEqual(len(result), 0)

    def test_metrics_error_tracking(self):
        """Test that metrics track validation errors."""
        reset_metrics()
        metrics = get_metrics()

        invalid_users = [
            {"id": 1},  # Invalid
            {"id": 2},  # Invalid
        ]

        store = UserStore(invalid_users)
        self.assertEqual(metrics.get_counter("validation_errors"), 2)

    def test_large_data_set(self):
        """Test handling large datasets."""
        users = []
        for i in range(1000):
            users.append({
                "id": i,
                "name": f"User{i}",
                "email": f"user{i}@example.com",
                "role": "User",
                "status": "Active",
                "join_date": "2023-01-01",
                "last_login": "2025-01-01",
            })

        store = UserStore(users)
        self.assertEqual(store.count(), 1000)

        # Test lookup is fast
        user = store.get_by_id(500)
        self.assertIsNotNone(user)
        self.assertEqual(user["name"], "User500")

    def test_special_characters_in_fields(self):
        """Test handling special characters."""
        user = {
            "id": 1,
            "name": "John O'Brien",
            "email": "john+test@example.com",
            "role": "User",
            "status": "Active",
            "join_date": "2023-01-01",
            "last_login": "2025-01-01",
        }

        store = UserStore([user])
        retrieved = store.get_by_id(1)
        self.assertEqual(retrieved["name"], "John O'Brien")
        self.assertEqual(retrieved["email"], "john+test@example.com")

    def test_unicode_support(self):
        """Test handling of unicode characters."""
        user = {
            "id": 1,
            "name": "João Silva",
            "email": "joao@example.com",
            "role": "User",
            "status": "Ativo",
            "join_date": "2023-01-01",
            "last_login": "2025-01-01",
        }

        store = UserStore([user])
        retrieved = store.get_by_id(1)
        self.assertEqual(retrieved["name"], "João Silva")

    def test_clear_store(self):
        """Test clearing the store."""
        users = [
            {"id": i, "name": f"User{i}", "email": f"user{i}@example.com", "role": "User",
             "status": "Active", "join_date": "2023-01-01", "last_login": "2025-01-01"}
            for i in range(10)
        ]

        store = UserStore(users)
        self.assertEqual(store.count(), 10)

        store.clear()
        self.assertEqual(store.count(), 0)


if __name__ == "__main__":
    unittest.main()
