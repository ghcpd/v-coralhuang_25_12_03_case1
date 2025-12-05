"""Metrics tracking for user display operations."""

from threading import Lock
from typing import Dict, Any


class Metrics:
    """Thread-safe metrics collection."""

    def __init__(self):
        self._counters: Dict[str, int] = {}
        self._timings: Dict[str, float] = {}
        self._lock = Lock()

    def increment(self, key: str, value: int = 1) -> None:
        """Increment a counter."""
        with self._lock:
            self._counters[key] = self._counters.get(key, 0) + value

    def record_timing(self, key: str, value: float) -> None:
        """Record a timing measurement."""
        with self._lock:
            self._timings[key] = value

    def get_counter(self, key: str) -> int:
        """Get counter value."""
        with self._lock:
            return self._counters.get(key, 0)

    def get_timing(self, key: str) -> float:
        """Get timing value."""
        with self._lock:
            return self._timings.get(key, 0.0)

    def get_all_counters(self) -> Dict[str, int]:
        """Get all counters."""
        with self._lock:
            return dict(self._counters)

    def get_all_timings(self) -> Dict[str, float]:
        """Get all timings."""
        with self._lock:
            return dict(self._timings)

    def reset(self) -> None:
        """Reset all metrics."""
        with self._lock:
            self._counters.clear()
            self._timings.clear()

    def get_summary(self) -> Dict[str, Any]:
        """Get a summary of all metrics."""
        with self._lock:
            return {
                "counters": dict(self._counters),
                "timings": dict(self._timings),
            }


# Global metrics instance
_metrics = Metrics()


def get_metrics() -> Metrics:
    """Get the global metrics instance."""
    return _metrics


def reset_metrics() -> None:
    """Reset global metrics."""
    _metrics.reset()
