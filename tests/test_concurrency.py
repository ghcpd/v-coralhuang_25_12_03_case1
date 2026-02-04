import threading

from user_display.store import UserStore


def test_concurrent_reads(many_users):
    store = UserStore(many_users)
    errors = []

    def lookup_worker():
        try:
            for i in range(1, 200):
                user = store.get_user_by_id(i)
                assert user is None or user["id"] == i
        except Exception as e:
            errors.append(e)

    def filter_worker():
        try:
            for _ in range(100):
                res = store.filter_users({"status": "Active"})
                assert isinstance(res, list)
        except Exception as e:
            errors.append(e)

    threads = [threading.Thread(target=lookup_worker) for _ in range(5)] + [threading.Thread(target=filter_worker) for _ in range(5)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert not errors
