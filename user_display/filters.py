"""Filtering strategies for user records."""

from .config import Config
from .errors import FilterError
from .logging_utils import get_logger

logger = get_logger()


class FilterStrategy:
    """Base class for filter strategies."""

    def apply(self, users, criteria):
        """Apply filter to users. Must be overridden."""
        raise NotImplementedError


class SimpleFilterStrategy(FilterStrategy):
    """Simple exact/substring matching filter."""

    def apply(self, users, criteria):
        """Filter users based on criteria dictionary."""
        if not criteria:
            return users

        filtered = []
        case_sensitive = Config.CASE_SENSITIVE_FILTERS

        for user in users:
            if self._matches(user, criteria, case_sensitive):
                filtered.append(user)

        return filtered

    def _matches(self, user, criteria, case_sensitive):
        """Check if user matches all criteria."""
        for key, value in criteria.items():
            user_value = user.get(key)

            if user_value is None:
                return False

            if key in ("role", "status"):
                # Exact match for categorical fields
                if case_sensitive:
                    if user_value != value:
                        return False
                else:
                    if str(user_value).lower() != str(value).lower():
                        return False
            else:
                # Substring match for text fields
                user_str = str(user_value).lower() if not case_sensitive else str(user_value)
                value_str = str(value).lower() if not case_sensitive else str(value)
                if value_str not in user_str:
                    return False

        return True


class AdvancedFilterStrategy(FilterStrategy):
    """Advanced filtering with operators and callbacks."""

    def __init__(self):
        """Initialize advanced filter strategy."""
        self.validators = []

    def add_validator(self, validator_func):
        """Add a custom validator function."""
        self.validators.append(validator_func)

    def apply(self, users, criteria):
        """Filter users with both simple criteria and custom validators."""
        simple_strategy = SimpleFilterStrategy()
        filtered = simple_strategy.apply(users, criteria)

        for validator in self.validators:
            try:
                filtered = [u for u in filtered if validator(u)]
            except Exception as e:
                logger.error(f"Validator raised exception: {e}")
                raise FilterError(f"Custom validator failed: {e}")

        return filtered


class FilterCache:
    """Cache filter results to avoid redundant filtering."""

    def __init__(self, max_entries=None):
        """Initialize filter cache."""
        if max_entries is None:
            max_entries = Config.MAX_CACHE_ENTRIES
        self.max_entries = max_entries
        self.cache = {}
        self.hit_count = 0
        self.miss_count = 0

    def _make_key(self, user_ids, criteria):
        """Create a cache key from user IDs and criteria."""
        user_id_str = ",".join(str(uid) for uid in sorted(user_ids))
        criteria_str = ",".join(f"{k}={v}" for k, v in sorted(criteria.items()))
        return f"{user_id_str}|{criteria_str}"

    def get(self, user_ids, criteria):
        """Get cached result if available."""
        if not Config.ENABLE_FILTER_CACHING:
            return None

        key = self._make_key(user_ids, criteria)
        if key in self.cache:
            self.hit_count += 1
            return self.cache[key]
        self.miss_count += 1
        return None

    def set(self, user_ids, criteria, result):
        """Store result in cache."""
        if not Config.ENABLE_FILTER_CACHING:
            return

        if len(self.cache) >= self.max_entries:
            # Remove oldest entry
            oldest_key = next(iter(self.cache))
            del self.cache[oldest_key]

        key = self._make_key(user_ids, criteria)
        self.cache[key] = result

    def clear(self):
        """Clear the cache."""
        self.cache.clear()
        self.hit_count = 0
        self.miss_count = 0


def get_filter_strategy(strategy_type="simple"):
    """Get a filter strategy by type."""
    if strategy_type == "advanced":
        return AdvancedFilterStrategy()
    return SimpleFilterStrategy()
