"""Performance tests for optimization verification."""

import unittest
import time
from user_display_optimized import display_users, filter_users, get_user_by_id
from user_display.metrics import get_metrics, reset_metrics


class TestPerformance(unittest.TestCase):
    """Test performance against targets."""

    def setUp(self):
        reset_metrics()
        # Generate test data
        self.users_1k = [
            {
                "id": i,
                "name": f"User{i}",
                "email": f"user{i}@example.com",
                "role": "User" if i % 10 else "Admin",
                "status": "Active" if i % 3 else "Inactive",
                "join_date": "2023-01-01",
                "last_login": "2025-01-01",
            }
            for i in range(1000)
        ]

        self.users_10k = [
            {
                "id": i,
                "name": f"User{i}",
                "email": f"user{i}@example.com",
                "role": "User" if i % 10 else "Admin",
                "status": "Active" if i % 3 else "Inactive",
                "join_date": "2023-01-01",
                "last_login": "2025-01-01",
            }
            for i in range(10000)
        ]

    def test_display_1000_users_under_100ms(self):
        """Test displaying 1000 users completes under 100ms."""
        start = time.time()
        result = display_users(self.users_1k)
        elapsed = (time.time() - start) * 1000  # Convert to ms

        self.assertLess(elapsed, 100.0, f"Display took {elapsed:.2f}ms, target < 100ms")
        self.assertGreater(len(result), 0)

    def test_display_10000_users(self):
        """Test displaying 10000 users."""
        start = time.time()
        result = display_users(self.users_10k)
        elapsed = (time.time() - start) * 1000

        # Should be reasonably fast (< 500ms for 10x the data)
        self.assertLess(elapsed, 500.0, f"Display took {elapsed:.2f}ms")
        self.assertGreater(len(result), 0)

    def test_filter_1000_users_under_10ms(self):
        """Test filtering 1000 users completes under 10ms."""
        start = time.time()
        result = filter_users(self.users_1k, {"role": "User", "status": "Active"})
        elapsed = (time.time() - start) * 1000

        self.assertLess(elapsed, 10.0, f"Filter took {elapsed:.2f}ms, target < 10ms")
        self.assertGreater(len(result), 0)

    def test_filter_10000_users(self):
        """Test filtering 10000 users."""
        start = time.time()
        result = filter_users(self.users_10k, {"role": "User", "status": "Active"})
        elapsed = (time.time() - start) * 1000

        # Should scale linearly
        self.assertLess(elapsed, 100.0, f"Filter took {elapsed:.2f}ms")
        self.assertGreater(len(result), 0)

    def test_lookup_by_id_under_1ms(self):
        """Test ID lookup completes under 1ms (after store construction)."""
        # Pre-construct to isolate lookup time
        from user_display.store import UserStore
        store = UserStore(self.users_1k)

        start = time.time()
        result = store.get_by_id(500)
        elapsed = (time.time() - start) * 1000

        self.assertLess(elapsed, 1.0, f"Lookup took {elapsed:.3f}ms, target < 1ms")
        self.assertIsNotNone(result)
        self.assertEqual(result["id"], 500)

    def test_lookup_by_id_large_dataset(self):
        """Test ID lookup on 10000 users is still fast."""
        # Pre-construct to isolate lookup time
        from user_display.store import UserStore
        store = UserStore(self.users_10k)

        start = time.time()
        result = store.get_by_id(5000)
        elapsed = (time.time() - start) * 1000

        # Should still be very fast (O(1) operation)
        self.assertLess(elapsed, 1.0, f"Lookup took {elapsed:.3f}ms")
        self.assertIsNotNone(result)

    def test_lookup_nonexistent_id(self):
        """Test lookup of non-existent ID is fast."""
        # Pre-construct to isolate lookup time
        from user_display.store import UserStore
        store = UserStore(self.users_1k)

        start = time.time()
        result = store.get_by_id(99999)
        elapsed = (time.time() - start) * 1000

        self.assertLess(elapsed, 1.0)
        self.assertIsNone(result)

    def test_no_artificial_delays(self):
        """Verify no artificial time.sleep() calls slow down operations."""
        start = time.time()
        display_users(self.users_1k)
        elapsed = time.time() - start

        # The original baseline uses time.sleep(0.01) per user
        # That would be ~10 seconds for 1000 users
        # We should be done in far less than 1 second
        self.assertLess(elapsed, 1.0, f"Display took {elapsed:.2f}s, likely has delays")


class TestMetrics(unittest.TestCase):
    """Test metrics collection."""

    def setUp(self):
        reset_metrics()

    def test_metrics_track_operations(self):
        """Test that metrics track operations."""
        users = [
            {
                "id": i,
                "name": f"User{i}",
                "email": f"user{i}@example.com",
                "role": "User",
                "status": "Active",
                "join_date": "2023-01-01",
                "last_login": "2025-01-01",
            }
            for i in range(10)
        ]

        metrics = get_metrics()
        reset_metrics()

        display_users(users)
        self.assertGreater(metrics.get_counter("display_operations"), 0)

        reset_metrics()
        get_user_by_id(users, 5)
        self.assertGreater(metrics.get_counter("id_lookup_operations"), 0)

        reset_metrics()
        filter_users(users, {"role": "User"})
        self.assertGreater(metrics.get_counter("filter_operations"), 0)


if __name__ == "__main__":
    unittest.main()
