import logging
from user_display.store import UserStore
from user_display.metrics import metrics
from user_display.logging_utils import get_logger


def test_malformed_records_do_not_crash(caplog):
    bad = [
        {"name": "NoID"},
        {"id": None, "name": "NoneID"},
        {"id": 1, "name": "Good"},
    ]

    caplog.set_level(logging.WARNING)
    metrics.reset()
    s = UserStore(bad)
    assert s.get_by_id(1) is not None
    # validation should have incremented missing-id counter
    assert metrics.get("missing_id") >= 1


def test_logging_marker():
    logger = get_logger("user_display.test")
    # Logger should be configured with [MARKER] formatter
    # Sending a single INFO to ensure no errors
    logger.info("hello world")
