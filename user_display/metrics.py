"""Lightweight in-memory metrics for user_display.

Used to count operations in tests and demonstrate behavior.
"""
from collections import Counter
from threading import RLock


class _Metrics:
    def __init__(self):
        self._c = Counter()
        self._lock = RLock()

    def inc(self, name: str, n: int = 1):
        with self._lock:
            self._c[name] += n

    def get(self, name: str):
        with self._lock:
            return self._c[name]

    def snapshot(self):
        with self._lock:
            return dict(self._c)

    def reset(self):
        with self._lock:
            self._c.clear()


metrics = _Metrics()
