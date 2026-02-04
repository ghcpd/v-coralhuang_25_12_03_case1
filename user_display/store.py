import threading
import copy
from functools import lru_cache
from .filters import (RoleFilter, StatusFilter, NameContainsFilter, EmailContainsFilter, CompositeFilter)
from .metrics import Metrics
from .logging_utils import get_logger
from .errors import MissingFieldError

logger = get_logger(__name__)


class UserStore:
    def __init__(self, users=None, case_sensitive=False, cache_enabled=True):
        self._lock = threading.RLock()
        self.users = list(users) if users else []
        self.case_sensitive = case_sensitive
        self.cache_enabled = cache_enabled
        self.metrics = Metrics()
        self._build_index()
        # small in-memory cache for filter results
        self._filter_cache = {}

    def _build_index(self):
        self._id_index = {}
        for u in self.users:
            uid = u.get("id")
            if uid is None:
                logger.warning("User missing id field; skipping: %s", u)
                self.metrics.incr("validation.errors")
                continue
            self._id_index[uid] = u
        logger.info("Index built with %d entries", len(self._id_index))

    def add_users(self, users):
        with self._lock:
            for u in users:
                self.users.append(u)
            self._build_index()
            self._clear_cache()

    def _clear_cache(self):
        with self._lock:
            self._filter_cache.clear()

    def snapshot(self):
        with self._lock:
            return copy.deepcopy(self)

    def __iter__(self):
        with self._lock:
            # return shallow copies to avoid accidental mutation
            return iter(list(self.users))

    def get_user_by_id(self, user_id):
        with self._lock:
            self.metrics.incr("lookups")
            return self._id_index.get(user_id)

    def _criteria_key(self, criteria: dict):
        if not criteria:
            return None
        # Make key hashable
        return tuple(sorted((k, str(v)) for k, v in criteria.items()))

    def filter_users(self, criteria: dict):
        """Return list of users matching criteria. Uses simple strategy mapping.
        criteria example: {"role":"User", "status":"Active", "name":"John"}
        """
        self.metrics.incr("filters.requested")
        key = self._criteria_key(criteria)
        if self.cache_enabled and key is not None and key in self._filter_cache:
            self.metrics.incr("filters.cache_hits")
            return list(self._filter_cache[key])

        strategies = []
        if not criteria:
            strategies = []
        else:
            if "role" in criteria:
                strategies.append(RoleFilter(criteria["role"]))
            if "status" in criteria:
                strategies.append(StatusFilter(criteria["status"]))
            if "name" in criteria:
                strategies.append(NameContainsFilter(criteria["name"], case_sensitive=self.case_sensitive))
            if "email" in criteria:
                strategies.append(EmailContainsFilter(criteria["email"], case_sensitive=self.case_sensitive))

        composite = CompositeFilter(strategies) if strategies else None

        results = []
        with self._lock:
            for u in self.users:
                try:
                    if composite is None or composite.matches(u):
                        results.append(u)
                except KeyError as e:
                    # Recover from malformed records
                    logger.warning("Malformed user record %s: %s", u, e)
                    self.metrics.incr("validation.errors")
                    continue

        if self.cache_enabled and key is not None:
            self._filter_cache[key] = list(results)
        self.metrics.incr("filters.completed")
        return results
