"""Concurrency tests for thread-safe operations."""

import unittest
import threading
import time
from typing import List

from user_display import UserStore, Config, MultiCriteriaFilter
from user_display_optimized import display_users, get_user_by_id


def generate_users(count: int):
    """Generate test users."""
    return [
        {
            "id": i,
            "name": f"User {i}",
            "email": f"user{i}@test.com",
            "role": "User" if i % 3 != 0 else "Admin",
            "status": "Active",
        }
        for i in range(count)
    ]


class TestConcurrency(unittest.TestCase):
    """Test thread-safe operations."""

    def test_concurrent_reads(self):
        """Test multiple threads can read simultaneously."""
        users = generate_users(100)
        store = UserStore(users)
        
        results = []
        errors = []
        
        def read_user(user_id: int):
            try:
                user = store.get_by_id(user_id)
                results.append(user)
            except Exception as e:
                errors.append(e)
        
        # Create 10 threads reading different users
        threads = []
        for i in range(10):
            t = threading.Thread(target=read_user, args=(i * 10,))
            threads.append(t)
            t.start()
        
        # Wait for all threads
        for t in threads:
            t.join()
        
        # No errors should occur
        self.assertEqual(len(errors), 0)
        # Should have successful reads
        self.assertEqual(len(results), 10)

    def test_concurrent_filters(self):
        """Test multiple threads can filter simultaneously."""
        users = generate_users(100)
        
        results = []
        errors = []
        
        def filter_users_thread(criteria):
            try:
                from user_display_optimized import filter_users
                filtered = filter_users(users, criteria)
                results.append(len(filtered))
            except Exception as e:
                errors.append(e)
        
        # Create threads with different filter criteria
        threads = []
        criteria_list = [
            {"role": "Admin"},
            {"status": "Active"},
            {"role": "User"},
        ]
        
        for criteria in criteria_list:
            t = threading.Thread(target=filter_users_thread, args=(criteria,))
            threads.append(t)
            t.start()
        
        # Wait for all threads
        for t in threads:
            t.join()
        
        # No errors should occur
        self.assertEqual(len(errors), 0)
        # Should have results from all threads
        self.assertEqual(len(results), 3)

    def test_concurrent_formatting(self):
        """Test multiple threads can format simultaneously."""
        users = generate_users(50)
        
        results = []
        errors = []
        
        def format_users_thread():
            try:
                output = display_users(users, show_all=True)
                results.append(len(output))
            except Exception as e:
                errors.append(e)
        
        # Create 5 threads formatting
        threads = []
        for _ in range(5):
            t = threading.Thread(target=format_users_thread)
            threads.append(t)
            t.start()
        
        # Wait for all threads
        for t in threads:
            t.join()
        
        # No errors should occur
        self.assertEqual(len(errors), 0)
        # All should produce same length output
        self.assertEqual(len(results), 5)
        self.assertTrue(all(r == results[0] for r in results))

    def test_snapshot_independence(self):
        """Test snapshots are independent across threads."""
        users = generate_users(50)
        store = UserStore(users)
        
        snapshots = []
        
        def create_snapshot():
            snap = store.snapshot()
            snapshots.append(snap)
        
        # Create 3 snapshots concurrently
        threads = []
        for _ in range(3):
            t = threading.Thread(target=create_snapshot)
            threads.append(t)
            t.start()
        
        for t in threads:
            t.join()
        
        # Should have 3 independent snapshots
        self.assertEqual(len(snapshots), 3)
        
        # Each should have same data but be independent objects
        for snap in snapshots:
            self.assertEqual(len(snap), len(store))
            self.assertIsNot(snap, store)

    def test_concurrent_lookups_same_id(self):
        """Test many threads looking up same user ID."""
        users = generate_users(100)
        store = UserStore(users)
        
        results = []
        target_id = 50
        
        def lookup():
            user = store.get_by_id(target_id)
            results.append(user)
        
        # 20 threads all looking up same ID
        threads = []
        for _ in range(20):
            t = threading.Thread(target=lookup)
            threads.append(t)
            t.start()
        
        for t in threads:
            t.join()
        
        # All should get same user
        self.assertEqual(len(results), 20)
        for user in results:
            self.assertIsNotNone(user)
            self.assertEqual(user["id"], target_id)

    def test_stress_test_mixed_operations(self):
        """Stress test with mixed read operations."""
        users = generate_users(200)
        store = UserStore(users)
        
        operation_count = [0]
        errors = []
        
        def mixed_operations():
            try:
                for _ in range(10):
                    # Random operations
                    store.get_by_id(50)
                    store.filter(lambda u: u["status"] == "Active")
                    _ = store.get_all()
                    operation_count[0] += 3
            except Exception as e:
                errors.append(e)
        
        # 10 threads doing mixed operations
        threads = []
        for _ in range(10):
            t = threading.Thread(target=mixed_operations)
            threads.append(t)
            t.start()
        
        for t in threads:
            t.join()
        
        # No errors should occur
        self.assertEqual(len(errors), 0)
        # Should have completed all operations
        self.assertEqual(operation_count[0], 300)  # 10 threads * 10 iterations * 3 ops


class TestCacheThreadSafety(unittest.TestCase):
    """Test cache behavior with concurrent access."""

    def test_concurrent_cache_access(self):
        """Test cache is thread-safe."""
        users = generate_users(100)
        config = Config(enable_cache=True)
        criteria = {"role": "Admin"}
        
        results = []
        
        def filter_with_cache():
            filter_obj = MultiCriteriaFilter(criteria, config=config)
            filtered = filter_obj.filter(users)
            results.append(len(filtered))
        
        # Multiple threads using same criteria
        threads = []
        for _ in range(10):
            t = threading.Thread(target=filter_with_cache)
            threads.append(t)
            t.start()
        
        for t in threads:
            t.join()
        
        # All should return same result
        self.assertEqual(len(results), 10)
        self.assertTrue(all(r == results[0] for r in results))


if __name__ == "__main__":
    unittest.main()
