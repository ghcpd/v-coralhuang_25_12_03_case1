"""Performance tests to verify optimization targets."""

import unittest
import time
from typing import List, Dict, Any

from user_display import UserStore, Config, MultiCriteriaFilter
from user_display.formatters import get_formatter
from user_display_optimized import display_users, filter_users, get_user_by_id


def generate_users(count: int) -> List[Dict[str, Any]]:
    """Generate test users."""
    users = []
    for i in range(count):
        users.append({
            "id": i,
            "name": f"User {i}",
            "email": f"user{i}@test.com",
            "role": "User" if i % 3 != 0 else "Admin",
            "status": "Active" if i % 5 != 0 else "Inactive",
            "join_date": "2024-01-01",
            "last_login": "2025-12-01",
        })
    return users


class TestPerformance(unittest.TestCase):
    """Performance tests to verify optimization targets."""

    def test_display_1000_users_under_100ms(self):
        """Test: Display 1,000 users in < 100ms."""
        users = generate_users(1000)
        
        start = time.perf_counter()
        output = display_users(users, show_all=True)
        elapsed = (time.perf_counter() - start) * 1000  # Convert to ms
        
        self.assertIsNotNone(output)
        self.assertLess(elapsed, 100, f"Display took {elapsed:.2f}ms (target: <100ms)")
        print(f"✓ Display 1,000 users: {elapsed:.2f}ms")

    def test_filter_1000_users_under_10ms(self):
        """Test: Filter 1,000 users in < 10ms."""
        users = generate_users(1000)
        criteria = {"role": "Admin", "status": "Active"}
        
        start = time.perf_counter()
        filtered = filter_users(users, criteria)
        elapsed = (time.perf_counter() - start) * 1000
        
        self.assertIsNotNone(filtered)
        self.assertLess(elapsed, 10, f"Filter took {elapsed:.2f}ms (target: <10ms)")
        print(f"✓ Filter 1,000 users: {elapsed:.2f}ms")

    def test_lookup_by_id_under_1ms(self):
        """Test: Lookup by ID in < 1ms."""
        users = generate_users(1000)
        
        start = time.perf_counter()
        user = get_user_by_id(users, 500)
        elapsed = (time.perf_counter() - start) * 1000
        
        self.assertIsNotNone(user)
        self.assertLess(elapsed, 1, f"Lookup took {elapsed:.2f}ms (target: <1ms)")
        print(f"✓ Lookup by ID: {elapsed:.2f}ms")

    def test_store_handles_10k_users(self):
        """Test: Store can handle 10,000 users efficiently."""
        users = generate_users(10000)
        
        start = time.perf_counter()
        store = UserStore(users)
        elapsed = (time.perf_counter() - start) * 1000
        
        self.assertEqual(len(store), 10000)
        print(f"✓ Load 10,000 users: {elapsed:.2f}ms")

    def test_filter_with_cache(self):
        """Test: Caching improves repeated filter performance."""
        users = generate_users(1000)
        criteria = {"role": "Admin"}
        config = Config(enable_cache=True)
        
        filter_obj = MultiCriteriaFilter(criteria, config=config)
        
        # First filter (cache miss)
        start1 = time.perf_counter()
        result1 = filter_obj.filter(users)
        elapsed1 = (time.perf_counter() - start1) * 1000
        
        # Second filter (cache hit)
        start2 = time.perf_counter()
        result2 = filter_obj.filter(users)
        elapsed2 = (time.perf_counter() - start2) * 1000
        
        self.assertEqual(len(result1), len(result2))
        # Cache should be faster (or at least not slower)
        self.assertLessEqual(elapsed2, elapsed1 * 1.1)  # Allow 10% variance
        print(f"✓ Filter with cache: {elapsed1:.2f}ms → {elapsed2:.2f}ms")

    def test_string_building_efficiency(self):
        """Test: String building uses join, not concatenation."""
        users = generate_users(1000)
        formatter = get_formatter("compact")
        
        start = time.perf_counter()
        output = formatter.format_users(users, show_total=True)
        elapsed = (time.perf_counter() - start) * 1000
        
        self.assertIsNotNone(output)
        # Should be very fast with join
        self.assertLess(elapsed, 50, f"Format took {elapsed:.2f}ms")
        print(f"✓ Format 1,000 users: {elapsed:.2f}ms")

    def test_large_dataset_operations(self):
        """Test: Operations on large datasets complete reasonably."""
        users = generate_users(5000)
        
        # Test display
        start = time.perf_counter()
        output = display_users(users, show_all=True)
        display_time = (time.perf_counter() - start) * 1000
        
        # Test filter
        start = time.perf_counter()
        filtered = filter_users(users, {"status": "Active"})
        filter_time = (time.perf_counter() - start) * 1000
        
        # Test lookup
        start = time.perf_counter()
        user = get_user_by_id(users, 2500)
        lookup_time = (time.perf_counter() - start) * 1000
        
        print(f"✓ 5,000 users - Display: {display_time:.2f}ms, Filter: {filter_time:.2f}ms, Lookup: {lookup_time:.2f}ms")
        
        # Sanity checks
        self.assertLess(display_time, 500)
        self.assertLess(filter_time, 50)
        self.assertLess(lookup_time, 5)


class TestScalability(unittest.TestCase):
    """Test scalability with varying dataset sizes."""

    def test_linear_scaling(self):
        """Test that operations scale linearly, not quadratically."""
        sizes = [100, 500, 1000]
        display_times = []
        
        for size in sizes:
            users = generate_users(size)
            
            start = time.perf_counter()
            output = display_users(users, show_all=True)
            elapsed = time.perf_counter() - start
            display_times.append(elapsed)
        
        # Check that time growth is roughly linear
        # Time for 1000 users should be ~10x time for 100 users (not 100x)
        ratio = display_times[2] / display_times[0]
        self.assertLess(ratio, 15, f"Scaling appears quadratic: {ratio:.2f}x")
        print(f"✓ Scaling ratio (100→1000 users): {ratio:.2f}x")


if __name__ == "__main__":
    # Run with verbose output to see timing details
    unittest.main(verbosity=2)
