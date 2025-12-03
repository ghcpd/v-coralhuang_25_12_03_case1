from user_display.store import UserStore


def test_snapshot(sample_users):
    store = UserStore(sample_users)
    snap = store.snapshot()
    assert len(snap) == len(store)
    assert snap.get_user_by_id(1) == store.get_user_by_id(1)


def test_iter_users_returns_copy(sample_users):
    store = UserStore(sample_users)
    it = store.iter_users()
    lst = list(it)
    assert len(lst) == len(store)
    # Modifying the returned list should not affect the store
    lst.append({"id": 999})
    assert len(store) == len(sample_users)
