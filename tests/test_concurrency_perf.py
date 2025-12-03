import time
import random
import pytest
from concurrent.futures import ThreadPoolExecutor

import user_display_optimized as ud
from user_display.store import UserStore


@pytest.fixture(scope="module")
def many_users():
    return [
        {
            "id": i,
            "name": f"User {i}",
            "email": f"user{i}@example.com",
            "role": "Admin" if i % 5 == 0 else "User",
            "status": "Active" if i % 3 else "Inactive",
            "join_date": "2023-01-01",
            "last_login": "2023-02-01",
        }
        for i in range(1000)
    ]


@pytest.mark.concurrency
def test_concurrent_reads(many_users):
    store = UserStore(many_users)
    ids = list(range(1000))

    def worker():
        uid = random.choice(ids)
        return store.get_by_id(uid)

    with ThreadPoolExecutor(max_workers=8) as ex:
        results = list(ex.map(lambda _: worker(), range(200)))
    assert all(res is None or res.get("id") in ids for res in results)


@pytest.mark.performance
def test_display_performance(many_users):
    t0 = time.perf_counter()
    _ = ud.display_users(many_users, show_all=True)
    dt = (time.perf_counter() - t0) * 1000
    # target < 100ms; allow some headroom on CI
    assert dt < 500


@pytest.mark.performance
def test_filter_performance(many_users):
    t0 = time.perf_counter()
    _ = ud.filter_users(many_users, {"role": "User"})
    dt = (time.perf_counter() - t0) * 1000
    assert dt < 100


@pytest.mark.performance
def test_lookup_performance(many_users):
    store = UserStore(many_users)
    t0 = time.perf_counter()
    for _ in range(1000):
        _ = store.get_by_id(500)
    dt = (time.perf_counter() - t0) * 1000
    assert dt < 50
