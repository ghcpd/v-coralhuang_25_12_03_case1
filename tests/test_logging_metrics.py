import pytest

from user_display.store import UserStore
from user_display.logging_utils import get_logger


@pytest.mark.filterwarnings("ignore::")
def test_logging_marker_present(malformed_users):
    _ = UserStore(malformed_users)
    logger = get_logger()
    fmt_strings = [
        getattr(h.formatter, "_fmt", "") for h in logger.handlers if getattr(h, "formatter", None)
    ]
    assert any("[MARKER]" in f for f in fmt_strings)


def test_metrics_counts(sample_users):
    store = UserStore(sample_users)
    store.get_user_by_id(1)
    store.filter_users({"role": "User"})
    snap = store.metrics.snapshot()
    assert snap.get("lookup_calls", 0) == 1
    assert snap.get("filter_calls", 0) >= 1
