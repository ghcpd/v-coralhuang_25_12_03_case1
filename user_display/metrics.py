import threading
from collections import Counter
from typing import Dict


class Metrics:
    """Thread-safe counter collection for operations, cache hits/misses, validation errors."""

    def __init__(self):
        self._counters = Counter()
        self._lock = threading.Lock()

    def inc(self, name: str, by: int = 1) -> None:
        with self._lock:
            self._counters[name] += by

    def get(self, name: str, default: int = 0) -> int:
        with self._lock:
            return self._counters.get(name, default)

    def snapshot(self) -> Dict[str, int]:
        with self._lock:
            return dict(self._counters)

    def reset(self) -> None:
        with self._lock:
            self._counters.clear()
