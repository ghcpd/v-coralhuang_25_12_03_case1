from collections import OrderedDict
from threading import RLock
from typing import Any, Dict, Iterable, List, Mapping, Optional, Tuple

from .config import Config, DEFAULT_CONFIG, default_validator
from .filters import FilterStrategy, SimpleCriteriaFilter
from .logging_utils import get_logger
from .metrics import (
    metrics as global_metrics,
    Metrics,
    LOOKUP,
    LOOKUP_HIT,
    LOOKUP_MISS,
    FILTER,
    FILTER_CACHE_HIT,
    FILTER_CACHE_MISS,
    VALIDATION_ERROR,
)


class UserStore:
    def __init__(
        self,
        users: Iterable[Mapping[str, Any]],
        config: Optional[Config] = None,
        validator=None,
        logger=None,
        metrics: Optional[Metrics] = None,
    ) -> None:
        self.config = config or DEFAULT_CONFIG
        self._validator = validator or default_validator
        self.logger = logger or get_logger(__name__)
        self.metrics = metrics or global_metrics
        self._lock = RLock()
        self._users: List[Mapping[str, Any]] = []
        self._id_index: Dict[Any, Mapping[str, Any]] = {}
        self._cache: "OrderedDict[Any, List[Mapping[str, Any]]]" = OrderedDict()
        self._load_users(users)

    def _load_users(self, users: Iterable[Mapping[str, Any]]) -> None:
        for user in users:
            try:
                valid, missing = self._validator(user)
            except Exception:
                valid, missing = False, ["<validator-error>"]
            if not valid:
                self.metrics.inc(VALIDATION_ERROR)
                self.logger.warning(f"Skipping invalid user; missing fields={missing}")
                continue
            self._users.append(user)
            uid = user.get("id")
            if uid is not None:
                self._id_index[uid] = user

    @staticmethod
    def _criteria_key(criteria: Mapping[str, Any]) -> Tuple[Tuple[str, Any], ...]:
        items = []
        for k, v in sorted(criteria.items(), key=lambda kv: kv[0]):
            try:
                hash(v)
                hv = v
            except Exception:
                hv = repr(v)
            items.append((k, hv))
        return tuple(items)

    def _cache_get(self, key):
        if not self.config.enable_filter_cache:
            return None
        with self._lock:
            if key in self._cache:
                self._cache.move_to_end(key)
                self.metrics.inc(FILTER_CACHE_HIT)
                return self._cache[key]
            self.metrics.inc(FILTER_CACHE_MISS)
            return None

    def _cache_set(self, key, value):
        if not self.config.enable_filter_cache:
            return
        with self._lock:
            self._cache[key] = value
            self._cache.move_to_end(key)
            if len(self._cache) > self.config.max_cache_size:
                self._cache.popitem(last=False)

    def get_by_id(self, user_id: Any) -> Optional[Mapping[str, Any]]:
        self.metrics.inc(LOOKUP)
        user = self._id_index.get(user_id)
        if user is not None:
            self.metrics.inc(LOOKUP_HIT)
        else:
            self.metrics.inc(LOOKUP_MISS)
        return user

    def filter(
        self,
        criteria: Mapping[str, Any],
        case_insensitive: Optional[bool] = None,
        strategy: Optional[FilterStrategy] = None,
        use_cache: bool = True,
    ) -> List[Mapping[str, Any]]:
        self.metrics.inc(FILTER)
        strat = strategy or SimpleCriteriaFilter()
        ci = self.config.case_insensitive if case_insensitive is None else case_insensitive
        cache_key = None
        if use_cache and self.config.enable_filter_cache:
            cache_key = (strat.name, ci, self._criteria_key(criteria))
            cached = self._cache_get(cache_key)
            if cached is not None:
                return cached
        result = strat.filter(self._users, criteria, ci)
        if cache_key is not None:
            self._cache_set(cache_key, result)
        return result

    def iter_users(self):
        with self._lock:
            return iter(list(self._users))

    def snapshot(self) -> "UserStore":
        with self._lock:
            return UserStore(list(self._users), config=self.config, validator=self._validator, logger=self.logger, metrics=self.metrics)

    def __len__(self) -> int:
        return len(self._users)
