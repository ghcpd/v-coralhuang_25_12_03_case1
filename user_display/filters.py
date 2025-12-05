"""Filtering strategies for user selection."""

from typing import List, Dict, Any, Callable, Optional
from .config import get_config
from .metrics import get_metrics


class FilterStrategy:
    """Base class for filter strategies."""

    def apply(self, users: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Apply filter to users."""
        raise NotImplementedError


class CriteriaFilterStrategy(FilterStrategy):
    """Filter based on simple criteria dictionary."""

    def __init__(self, criteria: Dict[str, Any]):
        self.criteria = criteria
        self._metrics = get_metrics()
        self._config = get_config()

    def apply(self, users: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Apply criteria filter to users."""
        result = []

        for user in users:
            if self._matches_criteria(user):
                result.append(user)

        self._metrics.increment("filter_operations")
        return result

    def _matches_criteria(self, user: Dict[str, Any]) -> bool:
        """Check if user matches criteria."""
        for key, value in self.criteria.items():
            user_value = user.get(key)

            if user_value is None:
                return False

            # Exact match or substring based on field type
            if isinstance(value, str) and isinstance(user_value, str):
                # Use substring matching for name/email fields, exact for others
                if key in ["name", "email"]:
                    if self._config.case_sensitive_filters:
                        if value not in user_value:
                            return False
                    else:
                        if value.lower() not in user_value.lower():
                            return False
                else:
                    # Exact match for role, status, etc.
                    if self._config.case_sensitive_filters:
                        if user_value != value:
                            return False
                    else:
                        if user_value.lower() != value.lower():
                            return False
            else:
                if user_value != value:
                    return False

        return True


class PredicateFilterStrategy(FilterStrategy):
    """Filter based on a custom predicate function."""

    def __init__(self, predicate: Callable[[Dict[str, Any]], bool]):
        self.predicate = predicate
        self._metrics = get_metrics()

    def apply(self, users: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Apply predicate filter to users."""
        result = []
        errors = 0

        for user in users:
            try:
                if self.predicate(user):
                    result.append(user)
            except Exception as e:
                errors += 1

        self._metrics.increment("filter_operations")
        if errors > 0:
            self._metrics.increment("filter_errors", errors)

        return result


class CompositeFilterStrategy(FilterStrategy):
    """Combine multiple filters with AND logic."""

    def __init__(self, *strategies: FilterStrategy):
        self.strategies = strategies
        self._metrics = get_metrics()

    def apply(self, users: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Apply all filters in sequence."""
        result = users
        for strategy in self.strategies:
            result = strategy.apply(result)
        return result


class CacheableFilterStrategy(FilterStrategy):
    """Wrap a filter strategy with optional caching."""

    def __init__(self, strategy: FilterStrategy):
        self.strategy = strategy
        self._cache: Dict[int, List[Dict[str, Any]]] = {}
        self._config = get_config()
        self._metrics = get_metrics()

    def apply(self, users: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Apply filter with caching if enabled."""
        if not self._config.enable_filter_cache:
            return self.strategy.apply(users)

        # Use list identity as cache key
        cache_key = id(users)

        if cache_key in self._cache:
            self._metrics.increment("cache_hits")
            return self._cache[cache_key]

        result = self.strategy.apply(users)

        # Manage cache size
        if len(self._cache) >= self._config.cache_max_size:
            # Simple eviction: remove first item
            first_key = next(iter(self._cache))
            del self._cache[first_key]

        self._cache[cache_key] = result
        self._metrics.increment("cache_misses")

        return result


def create_criteria_filter(criteria: Dict[str, Any]) -> FilterStrategy:
    """Factory function to create criteria filter."""
    if get_config().enable_filter_cache:
        return CacheableFilterStrategy(CriteriaFilterStrategy(criteria))
    return CriteriaFilterStrategy(criteria)
