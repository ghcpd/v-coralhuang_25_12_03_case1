"""User storage and indexing system."""

import threading
from .config import Config
from .errors import MalformedUserError
from .logging_utils import get_logger
from .metrics import get_metrics

logger = get_logger()
metrics = get_metrics()


class UserStore:
    """Thread-safe user storage with indexing and filtering capabilities."""

    def __init__(self):
        """Initialize user store."""
        self.users = []
        self.id_index = {}  # Map user_id -> user dict for O(1) lookup
        self.lock = threading.RLock()
        self._validate_user_record = self._create_validator()

    def _create_validator(self):
        """Create a validator function for user records."""
        def validate(user):
            if not isinstance(user, dict):
                raise MalformedUserError(f"User must be dict, got {type(user)}")
            for field in Config.REQUIRED_FIELDS:
                if field not in user:
                    logger.warning(f"User {user.get('id', 'unknown')} missing field: {field}")
            return True
        return validate

    def add_user(self, user):
        """Add a user to the store."""
        try:
            self._validate_user_record(user)
        except MalformedUserError as e:
            metrics.increment("malformed_records")
            logger.error(f"Malformed user record: {e}")
            raise

        with self.lock:
            # Update or insert
            user_id = user.get("id")
            if user_id in self.id_index:
                # Replace existing
                idx = next(i for i, u in enumerate(self.users) if u.get("id") == user_id)
                self.users[idx] = user
            else:
                self.users.append(user)
                self.id_index[user_id] = user

    def add_users(self, users):
        """Add multiple users to the store."""
        for user in users:
            try:
                self.add_user(user)
            except MalformedUserError:
                # Continue with next user
                continue

    def get_user_by_id(self, user_id):
        """Get a user by ID (O(1) lookup)."""
        metrics.increment("lookup_operations")
        with self.lock:
            return self.id_index.get(user_id)

    def get_all_users(self):
        """Get all users (snapshot)."""
        with self.lock:
            return self.users.copy()

    def get_user_count(self):
        """Get the number of users."""
        with self.lock:
            return len(self.users)

    def remove_user(self, user_id):
        """Remove a user by ID."""
        with self.lock:
            if user_id in self.id_index:
                user = self.id_index[user_id]
                self.users.remove(user)
                del self.id_index[user_id]
                return True
            return False

    def clear(self):
        """Clear all users."""
        with self.lock:
            self.users.clear()
            self.id_index.clear()

    def snapshot(self):
        """Create a snapshot of current users."""
        with self.lock:
            return self.users.copy()

    def iter_users(self):
        """Iterate over users thread-safely."""
        with self.lock:
            for user in self.users:
                yield user


# Global store instance
_global_store = None


def get_store():
    """Get the global user store instance."""
    global _global_store
    if _global_store is None:
        _global_store = UserStore()
    return _global_store
