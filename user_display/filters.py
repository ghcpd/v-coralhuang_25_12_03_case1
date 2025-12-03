"""Pluggable filter strategies for user queries."""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Callable, Optional
from functools import lru_cache

from .config import Config
from .metrics import global_metrics
from .logging_utils import default_logger


class FilterStrategy(ABC):
    """Base class for filter strategies."""

    def __init__(self, config: Optional[Config] = None):
        """
        Initialize the filter strategy.

        Args:
            config: Configuration instance
        """
        self._config = config or Config.default()

    @abstractmethod
    def matches(self, user: Dict[str, Any]) -> bool:
        """
        Check if a user matches the filter criteria.

        Args:
            user: User dictionary to check

        Returns:
            True if user matches criteria
        """
        pass


class FieldMatchFilter(FilterStrategy):
    """Filter that matches exact field values."""

    def __init__(self, field: str, value: Any, config: Optional[Config] = None):
        """
        Initialize field match filter.

        Args:
            field: Field name to match
            value: Value to match
            config: Configuration instance
        """
        super().__init__(config)
        self.field = field
        self.value = value

    def matches(self, user: Dict[str, Any]) -> bool:
        """Check if user field matches the expected value."""
        if self.field not in user:
            return False

        user_value = user[self.field]

        # String comparison with case sensitivity control
        if isinstance(self.value, str) and isinstance(user_value, str):
            if self._config.case_sensitive:
                return user_value == self.value
            else:
                return user_value.lower() == self.value.lower()

        # Direct comparison for non-strings
        return user_value == self.value


class SubstringMatchFilter(FilterStrategy):
    """Filter that matches substring in field values."""

    def __init__(self, field: str, substring: str, config: Optional[Config] = None):
        """
        Initialize substring match filter.

        Args:
            field: Field name to search in
            substring: Substring to search for
            config: Configuration instance
        """
        super().__init__(config)
        self.field = field
        self.substring = substring

    def matches(self, user: Dict[str, Any]) -> bool:
        """Check if user field contains the substring."""
        if self.field not in user:
            return False

        user_value = str(user[self.field])

        if self._config.case_sensitive:
            return self.substring in user_value
        else:
            return self.substring.lower() in user_value.lower()


class CompositeFilter(FilterStrategy):
    """Filter that combines multiple filters with AND/OR logic."""

    def __init__(
        self,
        filters: List[FilterStrategy],
        mode: str = "AND",
        config: Optional[Config] = None,
    ):
        """
        Initialize composite filter.

        Args:
            filters: List of filter strategies to combine
            mode: Combination mode - 'AND' or 'OR'
            config: Configuration instance
        """
        super().__init__(config)
        self.filters = filters
        self.mode = mode.upper()

    def matches(self, user: Dict[str, Any]) -> bool:
        """Check if user matches combined criteria."""
        if not self.filters:
            return True

        if self.mode == "AND":
            return all(f.matches(user) for f in self.filters)
        elif self.mode == "OR":
            return any(f.matches(user) for f in self.filters)
        else:
            # Default to AND
            return all(f.matches(user) for f in self.filters)


class PredicateFilter(FilterStrategy):
    """Filter based on a custom predicate function."""

    def __init__(
        self, predicate: Callable[[Dict[str, Any]], bool], config: Optional[Config] = None
    ):
        """
        Initialize predicate filter.

        Args:
            predicate: Function that takes a user and returns True/False
            config: Configuration instance
        """
        super().__init__(config)
        self.predicate = predicate

    def matches(self, user: Dict[str, Any]) -> bool:
        """Check if user matches predicate."""
        try:
            return self.predicate(user)
        except Exception as e:
            default_logger.error(f"Predicate filter error: {e}")
            return False


class MultiCriteriaFilter:
    """
    High-level filter for multiple criteria with caching support.

    This is the main filter used by the public API for backwards compatibility.
    """

    def __init__(self, criteria: Dict[str, Any], config: Optional[Config] = None):
        """
        Initialize multi-criteria filter.

        Args:
            criteria: Dictionary of field->value criteria
            config: Configuration instance
        """
        self._config = config or Config.default()
        self._criteria = criteria
        self._cache = {} if self._config.enable_cache else None
        self._build_strategy()

    def _build_strategy(self) -> None:
        """Build filter strategy from criteria."""
        filters = []

        for field, value in self._criteria.items():
            # Check if it's a substring match (contains search)
            # For backward compatibility, treat certain fields as substring matches
            if field in ["name", "email"]:
                filters.append(
                    SubstringMatchFilter(field, str(value), self._config)
                )
            else:
                # Exact match for other fields
                filters.append(FieldMatchFilter(field, value, self._config))

        # Combine all filters with AND logic
        if filters:
            self._strategy = CompositeFilter(filters, mode="AND", config=self._config)
        else:
            # No criteria - match all
            self._strategy = PredicateFilter(lambda u: True, self._config)

    def filter(self, users: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Filter users based on criteria.

        Args:
            users: List of user dictionaries

        Returns:
            List of matching users
        """
        if self._config.enable_metrics:
            global_metrics.increment("filter.operations")

        # Check cache
        cache_key = self._make_cache_key()
        if self._cache is not None and cache_key in self._cache:
            if self._config.enable_metrics:
                global_metrics.increment("filter.cache_hits")
            return self._cache[cache_key]

        # Filter users
        result = []
        for user in users:
            try:
                if self._strategy.matches(user):
                    result.append(user.copy())
            except Exception as e:
                default_logger.error(f"Filter error for user {user.get('id')}: {e}")
                if self._config.enable_metrics:
                    global_metrics.increment("filter.errors")

        # Cache result
        if self._cache is not None:
            # Implement simple LRU by clearing cache if it gets too large
            if len(self._cache) >= self._config.cache_max_size:
                self._cache.clear()
                if self._config.enable_metrics:
                    global_metrics.increment("filter.cache_clears")

            self._cache[cache_key] = result

            if self._config.enable_metrics:
                global_metrics.increment("filter.cache_misses")

        if self._config.enable_metrics:
            global_metrics.increment("filter.users_matched", len(result))

        return result

    def _make_cache_key(self) -> str:
        """Create a cache key from criteria."""
        # Sort items for consistent keys
        items = sorted(self._criteria.items())
        return str(items)


def create_filter_from_criteria(
    criteria: Dict[str, Any], config: Optional[Config] = None
) -> MultiCriteriaFilter:
    """
    Factory function to create filter from criteria dictionary.

    Args:
        criteria: Dictionary of field->value criteria
        config: Configuration instance

    Returns:
        MultiCriteriaFilter instance
    """
    return MultiCriteriaFilter(criteria, config)
