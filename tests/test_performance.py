import time
from user_display.user_display_optimized import display_users, filter_users, get_user_by_id


def generate_users(n):
    return [{"id": i, "name": f"User {i}", "email": f"user{i}@example.com", "role": "User", "status": "Active", "join_date": "2024-01-01", "last_login": "2025-01-01"} for i in range(n)]


def test_display_1000_timing():
    users = generate_users(1000)
    t0 = time.perf_counter()
    _ = display_users(users, show_all=False)
    t1 = time.perf_counter()
    elapsed_ms = (t1 - t0) * 1000
    assert elapsed_ms < 200, f"Display 1k too slow: {elapsed_ms}ms"


def test_filter_1000_timing():
    users = generate_users(1000)
    t0 = time.perf_counter()
    _ = filter_users(users, {"role": "User"})
    t1 = time.perf_counter()
    elapsed_ms = (t1 - t0) * 1000
    assert elapsed_ms < 50, f"Filter 1k too slow: {elapsed_ms}ms"


def test_lookup_1000_timing():
    users = generate_users(1000)
    t0 = time.perf_counter()
    _ = get_user_by_id(users, 999)
    t1 = time.perf_counter()
    elapsed_ms = (t1 - t0) * 1000
    assert elapsed_ms < 5, f"Lookup too slow: {elapsed_ms}ms"
