import threading
import time
from user_display.store import UserStore


def test_get_by_id(store):
    assert store.get_user_by_id(1)["name"] == "John Doe"
    assert store.get_user_by_id(999) is None


def test_filter_by_role(store):
    res = store.filter_users({"role": "Admin"})
    assert len(res) == 1


def test_malformed_record_does_not_crash():
    users = [{"name": "No ID"}, {"id": 5, "name": "Ok"}]
    s = UserStore(users=users)
    res = s.filter_users({})
    assert any(u.get("id") == 5 for u in res)


def test_concurrent_reads(sample_users):
    s = UserStore(users=sample_users * 100)
    results = []
    def worker(i):
        for _ in range(100):
            results.append(s.get_user_by_id(1))

    threads = [threading.Thread(target=worker, args=(i,)) for i in range(5)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    assert len(results) == 5 * 100
