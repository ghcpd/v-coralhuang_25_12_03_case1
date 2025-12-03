import copy
import threading
from contextlib import contextmanager
from typing import Dict, Iterable, Optional, Callable

from .config import Config, default_config
from .filters import filter_users as run_filter, get_strategy
from .formatters import format_users
from .logging_utils import get_logger, log_validation_error
from .metrics import Metrics
from .validators import default_validate_user


class RWLock:
    """A simple reader-writer lock allowing multiple concurrent readers and single writer."""

    def __init__(self):
        self._read_ready = threading.Condition(threading.Lock())
        self._readers = 0

    @contextmanager
    def read_lock(self):
        with self._read_ready:
            self._readers += 1
        try:
            yield
        finally:
            with self._read_ready:
                self._readers -= 1
                if self._readers == 0:
                    self._read_ready.notify_all()

    @contextmanager
    def write_lock(self):
        with self._read_ready:
            while self._readers > 0:
                self._read_ready.wait()
            yield


class UserStore:
    def __init__(
        self,
        users: Iterable[dict],
        config: Optional[Config] = None,
        validator: Callable = default_validate_user,
        metrics: Optional[Metrics] = None,
        logger=None,
        enable_cache: Optional[bool] = None,
    ):
        self._config = config or default_config()
        self._metrics = metrics or Metrics()
        self._logger = logger or get_logger(self._config.logging_marker)
        self._validator = validator
        self._lock = RWLock()
        self._enable_cache = enable_cache if enable_cache is not None else self._config.enable_filter_cache
        self._filter_cache: Dict = {}

        self._users = []
        self._id_index: Dict = {}

        self._load_users(users)

    def _load_users(self, users: Iterable[dict]):
        for user in users:
            valid, err = self._validator(
                user,
                required_id=self._config.validation_required_id,
                required_fields=self._config.validation_required_fields,
            )
            if not valid:
                self._metrics.inc("validation_errors")
                log_validation_error(self._logger, err or "Invalid user record")
                continue
            uid = user.get("id")
            if uid in self._id_index:
                self._metrics.inc("duplicate_ids")
                log_validation_error(self._logger, f"Duplicate id encountered: {uid}, overriding previous entry")
            self._users.append(user)
            self._id_index[uid] = user

    @property
    def metrics(self) -> Metrics:
        return self._metrics

    @property
    def config(self) -> Config:
        return self._config

    def __len__(self) -> int:
        return len(self._users)

    def get_user_by_id(self, user_id):
        with self._lock.read_lock():
            self._metrics.inc("lookup_calls")
            return self._id_index.get(user_id)

    def _make_cache_key(self, criteria: Dict, strategy: str, case_sensitive: bool):
        def make_hashable(v):
            try:
                hash(v)
                return v
            except Exception:
                return str(v)

        items = tuple(sorted((k, make_hashable(v)) for k, v in criteria.items()))
        return (strategy, case_sensitive, items)

    def filter_users(self, criteria: Dict, strategy: str = "default", case_sensitive: Optional[bool] = None, use_cache: Optional[bool] = None):
        if criteria is None:
            return []
        local_cfg = copy.copy(self._config)
        if case_sensitive is not None:
            local_cfg.case_sensitive = case_sensitive
        do_cache = self._enable_cache if use_cache is None else use_cache
        cache_key = None

        with self._lock.read_lock():
            if do_cache:
                cache_key = self._make_cache_key(criteria, strategy, local_cfg.case_sensitive)
                if cache_key in self._filter_cache:
                    self._metrics.inc("filter_cache_hits")
                    return self._filter_cache[cache_key]

            self._metrics.inc("filter_calls")
            result = run_filter(self._users, criteria, strategy=strategy, config=local_cfg)

            if do_cache:
                self._metrics.inc("filter_cache_misses")
                self._filter_cache[cache_key] = result
            return result

    def iter_users(self):
        with self._lock.read_lock():
            # return a shallow copy iterator to allow safe iteration without holding the lock
            return iter(list(self._users))

    def snapshot(self):
        with self._lock.read_lock():
            return UserStore(
                users=list(self._users),
                config=copy.copy(self._config),
                validator=self._validator,
                metrics=None,
                logger=self._logger,
                enable_cache=self._enable_cache,
            )

    def display_users(
        self,
        show_all: bool = True,
        verbose: bool = False,
        formatter: Optional[str] = None,
        include_fields=None,
        exclude_fields=None,
    ) -> str:
        fmt = formatter or self._config.default_formatter or "compact"
        with self._lock.read_lock():
            users = list(self._users)

        lines = []
        if verbose:
            for user in users:
                print("Processing user:", user.get("id", "N/A"))
                lines.append(user)
        # If not verbose we can use users list directly
        lines = users if not verbose else lines

        output = format_users(lines, formatter=fmt, include_fields=include_fields, exclude_fields=exclude_fields, show_all=show_all)
        if show_all:
            output += f"\n\nTotal users processed: {len(lines)}\n"
        return output

    def export_users_to_string(self, include_fields=None, exclude_fields=None) -> str:
        return self.display_users(show_all=False, verbose=False, formatter="export", include_fields=include_fields, exclude_fields=exclude_fields)
