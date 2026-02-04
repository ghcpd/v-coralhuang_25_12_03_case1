"""Concurrency tests for thread-safety."""

import unittest
import threading
import time
from user_display.store import UserStore
from user_display.metrics import get_metrics, reset_metrics


class TestConcurrency(unittest.TestCase):
    """Test concurrent access and thread-safety."""

    def setUp(self):
        reset_metrics()
        self.sample_users = [
            {
                "id": i,
                "name": f"User{i}",
                "email": f"user{i}@example.com",
                "role": "User",
                "status": "Active",
                "join_date": "2023-01-01",
                "last_login": "2025-01-01",
            }
            for i in range(100)
        ]

    def test_concurrent_reads(self):
        """Test multiple threads reading concurrently."""
        store = UserStore(self.sample_users)
        results = []
        errors = []

        def reader_thread(user_id):
            try:
                user = store.get_by_id(user_id)
                results.append((user_id, user is not None))
            except Exception as e:
                errors.append(e)

        threads = []
        for i in range(10):
            for user_id in range(0, 100, 10):
                t = threading.Thread(target=reader_thread, args=(user_id,))
                threads.append(t)
                t.start()

        for t in threads:
            t.join()

        self.assertEqual(len(errors), 0, f"Errors occurred: {errors}")
        self.assertEqual(len(results), 100)

    def test_concurrent_iteration(self):
        """Test concurrent iteration over store."""
        store = UserStore(self.sample_users)
        results = []
        errors = []

        def iterator_thread():
            try:
                count = 0
                for user in store:
                    count += 1
                results.append(count)
            except Exception as e:
                errors.append(e)

        threads = []
        for _ in range(5):
            t = threading.Thread(target=iterator_thread)
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

        self.assertEqual(len(errors), 0)
        # Each thread should see all users
        for count in results:
            self.assertEqual(count, 100)

    def test_concurrent_snapshots(self):
        """Test concurrent snapshot creation."""
        store = UserStore(self.sample_users)
        snapshots = []
        errors = []

        def snapshot_thread():
            try:
                snap = store.snapshot()
                snapshots.append(snap)
            except Exception as e:
                errors.append(e)

        threads = []
        for _ in range(5):
            t = threading.Thread(target=snapshot_thread)
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

        self.assertEqual(len(errors), 0)
        self.assertEqual(len(snapshots), 5)

    def test_concurrent_filter(self):
        """Test concurrent filtering."""
        store = UserStore(self.sample_users)
        results = []
        errors = []

        def filter_thread(role):
            try:
                filtered = store.filter(lambda u: u["role"] == role)
                results.append((role, len(filtered)))
            except Exception as e:
                errors.append(e)

        threads = []
        for _ in range(5):
            t = threading.Thread(target=filter_thread, args=("User",))
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

        self.assertEqual(len(errors), 0)
        # All should get same results
        for role, count in results:
            self.assertGreater(count, 0)

    def test_mixed_concurrent_operations(self):
        """Test mix of concurrent operations."""
        store = UserStore(self.sample_users)
        errors = []

        def mixed_operations(thread_id):
            try:
                # Read
                user = store.get_by_id(thread_id % 100)
                if user:
                    pass  # Verify read

                # Iterate
                for u in store:
                    pass

                # Filter
                filtered = store.filter(lambda u: u["id"] < 50)
            except Exception as e:
                errors.append((thread_id, e))

        threads = []
        for i in range(10):
            t = threading.Thread(target=mixed_operations, args=(i,))
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

        self.assertEqual(len(errors), 0, f"Errors: {errors}")


if __name__ == "__main__":
    unittest.main()
