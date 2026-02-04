from dataclasses import dataclass, field
from threading import Lock
from typing import Dict


@dataclass
class Metrics:
    _lock: Lock = field(default_factory=Lock, init=False, repr=False)
    counters: Dict[str, int] = field(default_factory=dict)

    def inc(self, name: str, value: int = 1) -> None:
        with self._lock:
            self.counters[name] = self.counters.get(name, 0) + value

    def get(self, name: str) -> int:
        with self._lock:
            return self.counters.get(name, 0)

    def to_dict(self) -> Dict[str, int]:
        with self._lock:
            return dict(self.counters)


metrics = Metrics()

# Common metric keys
LOOKUP = "lookup"
LOOKUP_HIT = "lookup_hit"
LOOKUP_MISS = "lookup_miss"
FILTER = "filter"
FILTER_CACHE_HIT = "filter_cache_hit"
FILTER_CACHE_MISS = "filter_cache_miss"
VALIDATION_ERROR = "validation_error"
