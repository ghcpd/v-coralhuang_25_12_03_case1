import time
from user_display.store import UserStore
from user_display_optimized import display_users, filter_users, get_user_by_id


def make_users(n):
    return [
        {"id": i, "name": f"User{i}", "email": f"u{i}@ex.com", "role": "User" if i % 2 == 0 else "Admin", "status": "Active"}
        for i in range(1, n + 1)
    ]


def test_display_1000_is_fast():
    users = make_users(1000)
    t0 = time.perf_counter()
    _ = display_users(users, show_all=False)
    t = (time.perf_counter() - t0) * 1000.0
    # target: < 100ms
    assert t < 100.0, f"display took {t:.2f}ms (expected < 100ms)"


def test_filter_1000_is_fast():
    users = make_users(1000)
    t0 = time.perf_counter()
    _ = filter_users(users, {"role": "User"})
    t = (time.perf_counter() - t0) * 1000.0
    assert t < 10.0, f"filter took {t:.2f}ms (expected < 10ms)"


def test_lookup_is_fast():
    users = make_users(1000)
    s = UserStore(users)
    t0 = time.perf_counter()
    _ = s.get_by_id(500)
    t = (time.perf_counter() - t0) * 1000.0
    assert t < 1.0, f"lookup took {t:.2f}ms (expected < 1ms)"
