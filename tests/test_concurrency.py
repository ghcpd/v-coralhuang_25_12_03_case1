"""Concurrency tests for the user_display module."""

import unittest
import threading
import time
from user_display import get_store


class TestConcurrency(unittest.TestCase):
    """Test thread-safe operations."""

    def setUp(self):
        """Set up test data."""
        self.store = get_store()
        self.store.clear()

    def tearDown(self):
        """Clean up after tests."""
        self.store.clear()

    def test_concurrent_reads(self):
        """Test multiple threads can read concurrently."""
        # Add test data
        users = [
            {"id": i, "name": f"User{i}", "email": f"user{i}@test.com", "role": "User", "status": "Active", "join_date": "2023-01-01", "last_login": "2025-12-01"}
            for i in range(100)
        ]
        self.store.add_users(users)

        results = []
        errors = []

        def reader_thread():
            try:
                for _ in range(50):
                    user = self.store.get_user_by_id(50)
                    results.append(user is not None)
            except Exception as e:
                errors.append(e)

        # Create multiple reader threads
        threads = [threading.Thread(target=reader_thread) for _ in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # All reads should succeed
        self.assertEqual(len(errors), 0)
        self.assertTrue(all(results))

    def test_concurrent_adds(self):
        """Test multiple threads can add users concurrently."""
        errors = []
        counter = {"value": 0}
        lock = threading.Lock()

        def writer_thread(start_id):
            try:
                for i in range(10):
                    user_id = start_id + i
                    user = {
                        "id": user_id,
                        "name": f"User{user_id}",
                        "email": f"user{user_id}@test.com",
                        "role": "User",
                        "status": "Active",
                        "join_date": "2023-01-01",
                        "last_login": "2025-12-01",
                    }
                    self.store.add_user(user)
                    with lock:
                        counter["value"] += 1
            except Exception as e:
                errors.append(e)

        # Create multiple writer threads with different ID ranges
        threads = [threading.Thread(target=writer_thread, args=(i * 10,)) for i in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # All adds should succeed
        self.assertEqual(len(errors), 0)
        self.assertEqual(counter["value"], 50)
        self.assertEqual(self.store.get_user_count(), 50)

    def test_concurrent_mixed_operations(self):
        """Test mix of reads and writes."""
        # Add initial data
        for i in range(50):
            user = {
                "id": i,
                "name": f"User{i}",
                "email": f"user{i}@test.com",
                "role": "User",
                "status": "Active",
                "join_date": "2023-01-01",
                "last_login": "2025-12-01",
            }
            self.store.add_user(user)

        errors = []
        read_count = {"value": 0}
        write_count = {"value": 0}
        lock = threading.Lock()

        def mixed_thread(thread_id):
            try:
                # Reads
                for _ in range(20):
                    user = self.store.get_user_by_id(thread_id % 50)
                    if user:
                        with lock:
                            read_count["value"] += 1

                # Writes
                for i in range(5):
                    user_id = 1000 + thread_id * 10 + i
                    user = {
                        "id": user_id,
                        "name": f"NewUser{user_id}",
                        "email": f"new{user_id}@test.com",
                        "role": "User",
                        "status": "Active",
                        "join_date": "2023-01-01",
                        "last_login": "2025-12-01",
                    }
                    self.store.add_user(user)
                    with lock:
                        write_count["value"] += 1
            except Exception as e:
                errors.append(e)

        # Create multiple mixed-operation threads
        threads = [threading.Thread(target=mixed_thread, args=(i,)) for i in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # All operations should succeed
        self.assertEqual(len(errors), 0)
        self.assertEqual(read_count["value"], 200)
        self.assertEqual(write_count["value"], 50)

    def test_snapshot_during_concurrent_operations(self):
        """Test snapshot creation while other threads are accessing data."""
        # Add initial data
        for i in range(20):
            user = {
                "id": i,
                "name": f"User{i}",
                "email": f"user{i}@test.com",
                "role": "User",
                "status": "Active",
                "join_date": "2023-01-01",
                "last_login": "2025-12-01",
            }
            self.store.add_user(user)

        snapshots = []
        errors = []

        def snapshot_thread():
            try:
                for _ in range(5):
                    snapshot = self.store.snapshot()
                    snapshots.append(len(snapshot))
                    time.sleep(0.001)
            except Exception as e:
                errors.append(e)

        def access_thread():
            try:
                for i in range(50):
                    self.store.get_user_by_id(i % 20)
            except Exception as e:
                errors.append(e)

        # Mix snapshot and access threads
        threads = [threading.Thread(target=snapshot_thread) for _ in range(2)]
        threads.extend([threading.Thread(target=access_thread) for _ in range(3)])

        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # All operations should succeed
        self.assertEqual(len(errors), 0)
        # Snapshots should be consistent
        self.assertTrue(all(s == 20 for s in snapshots))


if __name__ == "__main__":
    unittest.main()
