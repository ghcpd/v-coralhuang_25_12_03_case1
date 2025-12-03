from user_display.store import UserStore
from user_display.config import get_config
from user_display.metrics import metrics, FILTER_CACHE_HIT, FILTER_CACHE_MISS, LOOKUP_HIT, LOOKUP_MISS, VALIDATION_ERROR


def test_userstore_lookup_and_validation():
    metrics.counters.clear()
    users = [
        {"id": 1, "name": "A", "email": "a@example.com", "role": "Admin", "status": "Active", "join_date": "", "last_login": ""},
        {"id": 2, "name": "B", "role": "User", "status": "Active", "join_date": "", "last_login": ""},  # missing email
    ]
    store = UserStore(users)
    assert len(store) == 1  # invalid skipped
    assert metrics.get(VALIDATION_ERROR) == 1
    assert store.get_by_id(1)["name"] == "A"
    assert store.get_by_id(999) is None
    assert metrics.get(LOOKUP_HIT) >= 1
    assert metrics.get(LOOKUP_MISS) >= 1


def test_userstore_filter_cache():
    metrics.counters.clear()
    users = [
        {"id": i, "name": f"User{i}", "email": f"u{i}@x.com", "role": "User", "status": "Active", "join_date": "", "last_login": ""}
        for i in range(5)
    ]
    store = UserStore(users, config=get_config({"max_cache_size": 4}))
    criteria = {"role": "User"}
    first = store.filter(criteria)
    second = store.filter(criteria)
    assert first == second
    assert metrics.get(FILTER_CACHE_HIT) >= 1
    assert metrics.get(FILTER_CACHE_MISS) >= 1


def test_snapshot_clone_independent():
    users = [
        {"id": 1, "name": "A", "email": "a@example.com", "role": "Admin", "status": "Active", "join_date": "", "last_login": ""},
    ]
    store = UserStore(users)
    snap = store.snapshot()
    assert len(store) == len(snap) == 1
    assert store.get_by_id(1) == snap.get_by_id(1)
