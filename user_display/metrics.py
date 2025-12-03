"""Metrics collection for the user_display module."""

from .config import Config


class Metrics:
    """Collect and track operation metrics."""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self._initialized = True
        self.counters = {
            "display_operations": 0,
            "filter_operations": 0,
            "lookup_operations": 0,
            "export_operations": 0,
            "validation_errors": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "malformed_records": 0,
        }
        self.timings = {}

    def increment(self, counter, amount=1):
        """Increment a counter."""
        if Config.ENABLE_METRICS and counter in self.counters:
            self.counters[counter] += amount

    def record_timing(self, operation, duration):
        """Record timing for an operation."""
        if Config.ENABLE_METRICS:
            if operation not in self.timings:
                self.timings[operation] = []
            self.timings[operation].append(duration)

    def get_counter(self, counter):
        """Get counter value."""
        return self.counters.get(counter, 0)

    def get_averages(self):
        """Get average timings."""
        averages = {}
        for operation, durations in self.timings.items():
            if durations:
                averages[operation] = sum(durations) / len(durations)
        return averages

    def reset(self):
        """Reset all metrics."""
        for counter in self.counters:
            self.counters[counter] = 0
        self.timings.clear()

    def get_summary(self):
        """Get a summary of all metrics."""
        return {
            "counters": self.counters.copy(),
            "averages": self.get_averages(),
        }


def get_metrics():
    """Get the global metrics instance."""
    return Metrics()
