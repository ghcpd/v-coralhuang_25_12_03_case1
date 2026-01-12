"""High-performance user data store with O(1) lookups."""

from threading import RLock
from typing import Dict, List, Optional, Callable, Any
from copy import deepcopy

from .errors import ValidationError, UserNotFoundError
from .config import Config
from .logging_utils import default_logger
from .metrics import global_metrics


class UserStore:
    """
    Thread-safe user data store with O(1) ID lookup and efficient operations.

    This class provides:
    - O(1) user lookup by ID via hash map
    - Thread-safe reads and writes
    - Validation and error recovery
    - Snapshot/clone support
    - Efficient iteration
    """

    def __init__(self, users: Optional[List[Dict[str, Any]]] = None, config: Optional[Config] = None):
        """
        Initialize the user store.

        Args:
            users: Initial list of user dictionaries
            config: Configuration instance
        """
        self._config = config or Config.default()
        self._users: List[Dict[str, Any]] = []
        self._id_index: Dict[int, int] = {}  # user_id -> list index
        self._lock = RLock()

        if users:
            self.load_users(users)

    def _validate_user(self, user: Dict[str, Any], index: int) -> Optional[Dict[str, Any]]:
        """
        Validate and optionally fix a user record.

        Args:
            user: User dictionary to validate
            index: Index of user in list (for logging)

        Returns:
            Validated (and possibly fixed) user dictionary

        Raises:
            ValidationError: If validation fails and strict mode is enabled
        """
        if not isinstance(user, dict):
            msg = f"User at index {index} is not a dictionary"
            default_logger.error(msg)
            if self._config.strict_validation:
                raise ValidationError(msg)
            return None

        # Check for required fields
        missing_fields = [
            field for field in self._config.required_fields if field not in user
        ]

        if missing_fields:
            msg = f"User at index {index} missing fields: {missing_fields}"
            default_logger.warning(msg)

            if self._config.auto_fix_malformed:
                # Auto-fix with default values
                for field in missing_fields:
                    if field == "id":
                        user["id"] = index
                    elif field in ["name", "email", "role", "status"]:
                        user[field] = "UNKNOWN"
                    elif field in ["join_date", "last_login"]:
                        user[field] = "1970-01-01"
                    else:
                        user[field] = ""
                default_logger.info(f"Auto-fixed user at index {index}")
                if self._config.enable_metrics:
                    global_metrics.increment("validation.auto_fixed")
            elif self._config.strict_validation:
                raise ValidationError(msg)
            else:
                # Return None to skip this user
                if self._config.enable_metrics:
                    global_metrics.increment("validation.skipped")
                return None

        # Validate ID is present and can be converted to int
        try:
            user_id = int(user["id"])
            user["id"] = user_id  # Ensure it's stored as int
        except (ValueError, KeyError, TypeError):
            msg = f"User at index {index} has invalid ID: {user.get('id')}"
            default_logger.error(msg)
            if self._config.strict_validation:
                raise ValidationError(msg)
            if self._config.auto_fix_malformed:
                user["id"] = index
                if self._config.enable_metrics:
                    global_metrics.increment("validation.auto_fixed")
            else:
                return None

        if self._config.enable_metrics:
            global_metrics.increment("validation.passed")

        return user

    def load_users(self, users: List[Dict[str, Any]]) -> None:
        """
        Load users into the store with validation and indexing.

        Args:
            users: List of user dictionaries
        """
        with self._lock:
            self._users.clear()
            self._id_index.clear()

            for idx, user in enumerate(users):
                validated_user = self._validate_user(user, idx)
                if validated_user is not None:
                    list_index = len(self._users)
                    self._users.append(validated_user)
                    self._id_index[validated_user["id"]] = list_index

            default_logger.info(
                f"Loaded {len(self._users)} users (from {len(users)} records)"
            )
            if self._config.enable_metrics:
                global_metrics.increment("store.users_loaded", len(self._users))

    def get_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        """
        Get user by ID in O(1) time.

        Args:
            user_id: User ID to lookup

        Returns:
            User dictionary or None if not found
        """
        with self._lock:
            if self._config.enable_metrics:
                global_metrics.increment("store.lookups")

            list_index = self._id_index.get(user_id)
            if list_index is not None and 0 <= list_index < len(self._users):
                if self._config.enable_metrics:
                    global_metrics.increment("store.lookup_hits")
                return self._users[list_index].copy()

            if self._config.enable_metrics:
                global_metrics.increment("store.lookup_misses")
            return None

    def get_all(self) -> List[Dict[str, Any]]:
        """
        Get all users (shallow copy of list).

        Returns:
            List of user dictionaries
        """
        with self._lock:
            if self._config.enable_metrics:
                global_metrics.increment("store.get_all")
            return self._users.copy()

    def filter(
        self, predicate: Callable[[Dict[str, Any]], bool]
    ) -> List[Dict[str, Any]]:
        """
        Filter users based on a predicate function.

        Args:
            predicate: Function that takes a user and returns True to include it

        Returns:
            List of matching users
        """
        with self._lock:
            if self._config.enable_metrics:
                global_metrics.increment("store.filters")

            result = [user.copy() for user in self._users if predicate(user)]

            if self._config.enable_metrics:
                global_metrics.increment("store.filtered_users", len(result))

            return result

    def snapshot(self) -> "UserStore":
        """
        Create a deep copy snapshot of the store.

        Returns:
            New UserStore instance with copied data
        """
        with self._lock:
            if self._config.enable_metrics:
                global_metrics.increment("store.snapshots")

            new_store = UserStore(config=self._config)
            new_store._users = deepcopy(self._users)
            new_store._id_index = self._id_index.copy()
            return new_store

    def count(self) -> int:
        """
        Get the number of users in the store.

        Returns:
            User count
        """
        with self._lock:
            return len(self._users)

    def __len__(self) -> int:
        """Support len() function."""
        return self.count()

    def __iter__(self):
        """Support iteration over users."""
        with self._lock:
            # Create snapshot for safe iteration
            return iter(self._users.copy())
