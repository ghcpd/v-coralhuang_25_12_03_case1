import threading
from user_display.store import UserStore
from user_display.filters import CriteriaFilter


def sample_users(n=5):
    return [
        {"id": i, "name": f"User{i}", "email": f"u{i}@ex.com", "role": "User" if i % 2 == 0 else "Admin", "status": "Active"}
        for i in range(1, n + 1)
    ]


def test_get_by_id():
    users = sample_users(10)
    s = UserStore(users)
    assert s.get_by_id(5)["id"] == 5
    assert s.get_by_id(999) is None


def test_filter_criteria():
    users = sample_users(10)
    s = UserStore(users, case_sensitive=False)
    results = s.filter(criteria={"role": "User", "status": "Active"})
    # role == "User" occurs for even ids among sample_users
    assert all(r["role"] == "User" for r in results)


def test_filter_object():
    users = sample_users(6)
    f = CriteriaFilter({"name": "user1"}, case_sensitive=False)
    s = UserStore(users)
    out = s.filter(filter_obj=f)
    assert any("user1" in u["name"].lower() for u in out)


def test_concurrent_reads():
    users = sample_users(1000)
    s = UserStore(users)

    def reader():
        for i in range(1, 50):
            s.get_by_id(i)
            s.iter()

    threads = [threading.Thread(target=reader) for _ in range(10)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    # If we reached here without exception, thread-safety is OK for reads
    assert s.get_by_id(1)["id"] == 1
