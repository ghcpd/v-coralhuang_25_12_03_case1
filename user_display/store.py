"""User data storage with indexing and filtering capabilities."""

from typing import List, Dict, Any, Optional
from threading import RLock
import copy

from .errors import InvalidUserDataError, UserNotFoundError
from .logging_utils import log_warning, log_debug
from .metrics import get_metrics
from .config import get_config


REQUIRED_FIELDS = {"id", "name", "email", "role", "status", "join_date", "last_login"}


class UserStore:
    """Thread-safe user data store with indexing and filtering."""

    def __init__(self, users: Optional[List[Dict[str, Any]]] = None):
        """Initialize store with optional user list."""
        self._users: List[Dict[str, Any]] = []
        self._id_index: Dict[Any, int] = {}  # Maps user_id to index in _users
        self._lock = RLock()
        self._metrics = get_metrics()

        if users:
            self.add_users(users)

    def add_users(self, users: List[Dict[str, Any]]) -> None:
        """Add multiple users to the store."""
        config = get_config()
        for user in users:
            if config.skip_malformed_records:
                try:
                    self.add_user(user)
                except InvalidUserDataError:
                    log_warning(f"Skipping malformed user record: {user}")
                    self._metrics.increment("validation_errors")
            else:
                self.add_user(user)

    def add_user(self, user: Dict[str, Any]) -> None:
        """Add a single user to the store."""
        config = get_config()

        if config.validate_on_insert:
            self._validate_user(user)

        with self._lock:
            user_id = user.get("id")
            if user_id in self._id_index:
                # Update existing user
                idx = self._id_index[user_id]
                self._users[idx] = copy.deepcopy(user)
                self._metrics.increment("updates")
            else:
                # Add new user
                self._id_index[user_id] = len(self._users)
                self._users.append(copy.deepcopy(user))
                self._metrics.increment("inserts")

    def get_by_id(self, user_id: Any) -> Optional[Dict[str, Any]]:
        """Get a user by ID in O(1) time."""
        with self._lock:
            if user_id not in self._id_index:
                self._metrics.increment("lookups_miss")
                return None

            idx = self._id_index[user_id]
            self._metrics.increment("lookups_hit")
            return copy.deepcopy(self._users[idx])

    def get_all(self) -> List[Dict[str, Any]]:
        """Get all users as a copy."""
        with self._lock:
            return [copy.deepcopy(user) for user in self._users]

    def count(self) -> int:
        """Get the number of users."""
        with self._lock:
            return len(self._users)

    def snapshot(self) -> "UserStore":
        """Create a snapshot (deep copy) of the store."""
        with self._lock:
            new_store = UserStore()
            new_store._users = [copy.deepcopy(user) for user in self._users]
            new_store._id_index = dict(self._id_index)
            return new_store

    def filter(self, predicate) -> List[Dict[str, Any]]:
        """Filter users based on a predicate function."""
        with self._lock:
            result = []
            for user in self._users:
                try:
                    if predicate(user):
                        result.append(copy.deepcopy(user))
                except Exception as e:
                    log_warning(f"Error evaluating predicate on user {user.get('id')}: {e}")
                    self._metrics.increment("filter_errors")
            return result

    def _validate_user(self, user: Dict[str, Any]) -> None:
        """Validate user data structure."""
        if not isinstance(user, dict):
            raise InvalidUserDataError("User must be a dictionary")

        missing_fields = REQUIRED_FIELDS - set(user.keys())
        if missing_fields:
            raise InvalidUserDataError(f"Missing required fields: {missing_fields}")

        # Validate field types
        if not isinstance(user.get("id"), (int, str)):
            raise InvalidUserDataError(f"Invalid ID type: {type(user.get('id'))}")

        for field in ["name", "email", "role", "status", "join_date", "last_login"]:
            if not isinstance(user.get(field), str):
                raise InvalidUserDataError(f"Field '{field}' must be a string")

    def clear(self) -> None:
        """Clear all users."""
        with self._lock:
            self._users.clear()
            self._id_index.clear()

    def __len__(self) -> int:
        """Get the number of users."""
        return self.count()

    def __iter__(self):
        """Iterate over users (thread-safe snapshot)."""
        with self._lock:
            users_copy = [copy.deepcopy(user) for user in self._users]
        return iter(users_copy)
