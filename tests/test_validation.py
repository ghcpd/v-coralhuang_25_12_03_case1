from user_display.store import UserStore


def test_malformed_records_skipped(malformed_users):
    store = UserStore(malformed_users)
    # Users missing required 'id' are skipped; partial records are accepted with placeholders
    assert len(store) == 2
    snap = store.metrics.snapshot()
    assert snap.get("validation_errors", 0) >= 1
