"""Thread-safe user store with indexing, filtering and snapshot support.

Designed for fast lookups and efficient iteration.
"""
from typing import Iterable, Dict, Any, List, Optional
from threading import RLock
from .filters import BaseFilter, CriteriaFilter
from .logging_utils import get_logger
from .metrics import metrics
from .errors import UserValidationError

logger = get_logger(__name__)


class UserStore:
    def __init__(self, users: Iterable[Dict[str, Any]], validate: bool = True, cache_filters: bool = True, validator=None, case_sensitive=False):
        self._lock = RLock()
        self._raw = []
        self._index = {}
        self._cache = {} if cache_filters else None
        self.validator = validator
        self.case_sensitive = case_sensitive

        self._load(users, validate)

    def _load(self, users: Iterable[Dict[str, Any]], validate: bool):
        with self._lock:
            self._raw = []
            self._index = {}
            for u in users:
                # graceful validation
                if validate and self.validator:
                    try:
                        self.validator(u)
                    except Exception as exc:
                        metrics.inc("validation_errors")
                        logger.warning("Skipping invalid user: %s", exc)
                        continue

                uid = u.get("id")
                if uid is None:
                    metrics.inc("missing_id")
                    logger.warning("Skipping user missing id: %r", u)
                    continue

                self._raw.append(u)
                self._index[uid] = u

            metrics.inc("store_loaded", len(self._raw))

    def get_by_id(self, user_id) -> Optional[Dict[str, Any]]:
        # O(1) lookup, thread-safe
        with self._lock:
            metrics.inc("lookups")
            return self._index.get(user_id)

    def iter(self) -> Iterable[Dict[str, Any]]:
        # return a snapshot iterator of the current list
        with self._lock:
            # return a shallow copy to avoid external mutations
            return list(self._raw)

    def snapshot(self) -> List[Dict[str, Any]]:
        with self._lock:
            return [dict(u) for u in self._raw]

    def filter(self, filter_obj: Optional[BaseFilter] = None, criteria: Optional[Dict] = None):
        # Accept either a filter object or a criteria dict
        key = None
        if filter_obj is None and criteria is not None:
            filter_obj = CriteriaFilter(criteria, case_sensitive=self.case_sensitive)
            key = tuple(sorted(criteria.items()))

        # Try cache
        if self._cache is not None and key is not None:
            cached = self._cache.get(key)
            if cached is not None:
                metrics.inc("cache_hits")
                return list(cached)

        with self._lock:
            metrics.inc("filters")
            results = [u for u in self._raw if filter_obj.match(u)] if filter_obj else list(self._raw)

            if self._cache is not None and key is not None:
                self._cache[key] = list(results)

            return results
