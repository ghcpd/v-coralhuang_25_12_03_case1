import time

from user_display.store import UserStore


DISPLAY_THRESHOLD_SEC = 0.2  # 200ms for 1k users
FILTER_THRESHOLD_SEC = 0.05  # 50ms
LOOKUP_THRESHOLD_SEC = 0.002  # 2ms average


def test_performance_sanity(many_users):
    store = UserStore(many_users)

    start = time.perf_counter()
    _ = store.display_users(show_all=False, verbose=False)
    display_time = time.perf_counter() - start
    assert display_time < DISPLAY_THRESHOLD_SEC

    start = time.perf_counter()
    _ = store.filter_users({"role": "Admin"})
    filter_time = time.perf_counter() - start
    assert filter_time < FILTER_THRESHOLD_SEC

    # measure lookup avg over many operations
    start = time.perf_counter()
    for i in range(1, 1001):
        _ = store.get_user_by_id(i)
    lookup_time_total = time.perf_counter() - start
    avg_lookup = lookup_time_total / 1000.0
    assert avg_lookup < LOOKUP_THRESHOLD_SEC
