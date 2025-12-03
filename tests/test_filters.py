from user_display.store import UserStore


def test_multi_criteria_filter(sample_users):
    store = UserStore(sample_users)
    criteria = {"role": "User", "status": "Active"}
    filtered = store.filter_users(criteria)
    assert all(u["role"] == "User" and u["status"] == "Active" for u in filtered)


def test_case_insensitive_name_filter(sample_users):
    store = UserStore(sample_users)
    filtered = store.filter_users({"name": "john"})
    assert any("John" in u["name"] for u in filtered)


def test_case_sensitive_name_filter(sample_users):
    store = UserStore(sample_users)
    filtered = store.filter_users({"name": "john"}, case_sensitive=True)
    # No lowercase "john" in sample data
    assert filtered == []


def test_filter_cache_hits(many_users):
    store = UserStore(many_users)
    criteria = {"role": "Admin"}
    first = store.filter_users(criteria)
    second = store.filter_users(criteria)  # should hit cache
    assert first == second
    metrics = store.metrics.snapshot()
    assert metrics.get("filter_cache_hits", 0) >= 1
