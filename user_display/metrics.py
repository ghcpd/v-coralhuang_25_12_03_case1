"""Metrics tracking for performance monitoring."""

from threading import Lock
from typing import Dict
from collections import defaultdict


class Metrics:
    """Thread-safe metrics collector for operation tracking."""

    def __init__(self):
        self._counters: Dict[str, int] = defaultdict(int)
        self._lock = Lock()

    def increment(self, name: str, amount: int = 1) -> None:
        """
        Increment a counter by the specified amount.

        Args:
            name: Counter name
            amount: Amount to increment (default: 1)
        """
        with self._lock:
            self._counters[name] += amount

    def get(self, name: str) -> int:
        """
        Get current value of a counter.

        Args:
            name: Counter name

        Returns:
            Current counter value
        """
        with self._lock:
            return self._counters[name]

    def get_all(self) -> Dict[str, int]:
        """
        Get snapshot of all counters.

        Returns:
            Dictionary of all counter values
        """
        with self._lock:
            return dict(self._counters)

    def reset(self, name: str | None = None) -> None:
        """
        Reset counter(s) to zero.

        Args:
            name: Counter name to reset, or None to reset all
        """
        with self._lock:
            if name is None:
                self._counters.clear()
            elif name in self._counters:
                self._counters[name] = 0

    def summary(self) -> str:
        """
        Generate a formatted summary of all metrics.

        Returns:
            Multi-line string with all counter values
        """
        with self._lock:
            if not self._counters:
                return "No metrics recorded"

            lines = ["Metrics Summary:"]
            for name, value in sorted(self._counters.items()):
                lines.append(f"  {name}: {value}")
            return "\n".join(lines)


# Global metrics instance
global_metrics = Metrics()
