import logging

from user_display.logging_utils import get_logger, LOG_MARKER
from user_display.store import UserStore
from user_display.metrics import metrics, LOOKUP, FILTER


def test_logger_includes_marker(caplog):
    logger = get_logger("user_display.test")
    with caplog.at_level(logging.INFO):
        logger.info("hello")
    assert LOG_MARKER in caplog.text


def test_metrics_increment():
    metrics.counters.clear()
    users = [
        {"id": 1, "name": "A", "email": "a@example.com", "role": "Admin", "status": "Active", "join_date": "", "last_login": ""}
    ]
    store = UserStore(users)
    store.get_by_id(1)
    store.filter({"role": "Admin"})
    assert metrics.get(LOOKUP) >= 1
    assert metrics.get(FILTER) >= 1
