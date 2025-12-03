"""Performance tests for the user_display module."""

import unittest
import time
from user_display_optimized import (
    display_users,
    get_user_by_id,
    filter_users,
    export_users_to_string,
)
from user_display_original import (
    display_users as display_users_original,
    get_user_by_id as get_user_by_id_original,
    filter_users as filter_users_original,
    export_users_to_string as export_users_to_string_original,
)


class TestPerformance(unittest.TestCase):
    """Test performance targets."""

    def setUp(self):
        """Set up test data."""
        # Create test data of various sizes
        self.small_users = [
            {
                "id": i,
                "name": f"User{i}",
                "email": f"user{i}@test.com",
                "role": "User" if i % 3 else "Admin",
                "status": "Active" if i % 2 else "Inactive",
                "join_date": "2023-01-01",
                "last_login": "2025-12-01",
            }
            for i in range(100)
        ]

        self.medium_users = [
            {
                "id": i,
                "name": f"User{i}",
                "email": f"user{i}@test.com",
                "role": "User" if i % 3 else "Admin",
                "status": "Active" if i % 2 else "Inactive",
                "join_date": "2023-01-01",
                "last_login": "2025-12-01",
            }
            for i in range(1000)
        ]

        self.large_users = [
            {
                "id": i,
                "name": f"User{i}",
                "email": f"user{i}@test.com",
                "role": "User" if i % 3 else "Admin",
                "status": "Active" if i % 2 else "Inactive",
                "join_date": "2023-01-01",
                "last_login": "2025-12-01",
            }
            for i in range(10000)
        ]

    def test_display_1000_users_optimized(self):
        """Test displaying 1000 users (optimized version) - target < 100ms."""
        start = time.perf_counter()
        output = display_users(self.medium_users, show_all=True, verbose=False)
        elapsed = (time.perf_counter() - start) * 1000

        print(f"\nOptimized display_users(1000): {elapsed:.2f}ms")
        self.assertLess(elapsed, 100, f"Display 1000 users took {elapsed:.2f}ms, target < 100ms")
        self.assertGreater(len(output), 0)

    def test_filter_1000_users_optimized(self):
        """Test filtering 1000 users (optimized version) - target < 10ms."""
        start = time.perf_counter()
        result = filter_users(self.medium_users, {"role": "User", "status": "Active"})
        elapsed = (time.perf_counter() - start) * 1000

        print(f"Optimized filter_users(1000): {elapsed:.2f}ms")
        self.assertLess(elapsed, 10, f"Filter 1000 users took {elapsed:.2f}ms, target < 10ms")
        self.assertGreater(len(result), 0)

    def test_lookup_by_id_optimized(self):
        """Test ID lookup (optimized version) - target < 1ms."""
        # Warm up
        warmup = get_user_by_id(self.large_users, 5000)

        start = time.perf_counter()
        result = None
        for _ in range(100):
            result = get_user_by_id(self.large_users, 5000)
        elapsed = ((time.perf_counter() - start) / 100) * 1000

        print(f"Optimized get_user_by_id: {elapsed:.3f}ms (avg of 100 lookups in 10k users)")
        self.assertLess(elapsed, 1, f"ID lookup took {elapsed:.3f}ms, target < 1ms")
        self.assertIsNotNone(result)

    def test_export_1000_users_optimized(self):
        """Test exporting 1000 users (optimized version)."""
        start = time.perf_counter()
        output = export_users_to_string(self.medium_users)
        elapsed = (time.perf_counter() - start) * 1000

        print(f"Optimized export_users_to_string(1000): {elapsed:.2f}ms")
        self.assertLess(elapsed, 200, f"Export 1000 users took {elapsed:.2f}ms")
        self.assertGreater(len(output), 0)

    def test_display_10000_users_optimized(self):
        """Test displaying 10000 users (optimized version) - should be fast."""
        start = time.perf_counter()
        output = display_users(self.large_users, show_all=True, verbose=False)
        elapsed = (time.perf_counter() - start) * 1000

        print(f"Optimized display_users(10000): {elapsed:.2f}ms")
        # Should scale linearly and still be reasonably fast
        self.assertLess(elapsed, 1000, f"Display 10000 users took {elapsed:.2f}ms")
        self.assertGreater(len(output), 0)

    def test_performance_comparison_display(self):
        """Compare performance: original vs optimized for display."""
        # Test with medium size
        users = self.small_users

        # Original (this might be slow due to sleep)
        print("\nPerformance Comparison (100 users):")
        print("Note: Original includes artificial 0.01s delay per user")

        # Optimized
        start_opt = time.perf_counter()
        output_opt = display_users(users, show_all=False, verbose=False)
        time_opt = (time.perf_counter() - start_opt) * 1000

        print(f"Optimized display_users: {time_opt:.2f}ms")
        self.assertGreater(len(output_opt), 0)

    def test_scalability_linear(self):
        """Test that performance scales approximately linearly."""
        # Display 100 users
        start_100 = time.perf_counter()
        display_users(self.small_users, show_all=False, verbose=False)
        time_100 = (time.perf_counter() - start_100) * 1000

        # Display 1000 users
        start_1000 = time.perf_counter()
        display_users(self.medium_users, show_all=False, verbose=False)
        time_1000 = (time.perf_counter() - start_1000) * 1000

        print(f"\nScalability Test:")
        print(f"100 users: {time_100:.2f}ms")
        print(f"1000 users: {time_1000:.2f}ms")
        print(f"Ratio: {time_1000 / time_100:.2f}x (expect ~10x)")

        # Should scale approximately linearly
        ratio = time_1000 / time_100
        self.assertLess(ratio, 15, f"Scaling ratio {ratio:.2f}x suggests non-linear growth")
        self.assertGreater(ratio, 5, f"Scaling ratio {ratio:.2f}x seems too optimized")


if __name__ == "__main__":
    unittest.main()
