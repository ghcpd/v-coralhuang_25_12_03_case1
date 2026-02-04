from typing import Dict, Iterable, Callable, Optional
from .config import Config


class FilterStrategy:
    name: str = "base"

    def matches(self, user: dict, criteria: Dict, config: Config) -> bool:
        raise NotImplementedError


class DefaultFilterStrategy(FilterStrategy):
    name = "default"

    def matches(self, user: dict, criteria: Dict, config: Config) -> bool:
        case_sensitive = config.case_sensitive
        for key, value in criteria.items():
            if key not in user:
                return False
            user_val = user.get(key, "")

            # substring match for string fields name/email by default
            if isinstance(user_val, str) and isinstance(value, str) and key in ("name", "email"):
                if case_sensitive:
                    if value not in user_val:
                        return False
                else:
                    if value.lower() not in user_val.lower():
                        return False
            else:
                if case_sensitive:
                    if user_val != value:
                        return False
                else:
                    # Case-insensitive compare for strings
                    if isinstance(user_val, str) and isinstance(value, str):
                        if user_val.lower() != value.lower():
                            return False
                    else:
                        if user_val != value:
                            return False
        return True


_strategies: Dict[str, FilterStrategy] = {DefaultFilterStrategy.name: DefaultFilterStrategy()}


def register_strategy(name: str, strategy: FilterStrategy) -> None:
    _strategies[name] = strategy


def get_strategy(name: str) -> FilterStrategy:
    return _strategies.get(name, _strategies[DefaultFilterStrategy.name])


def filter_users(
    users: Iterable[dict],
    criteria: Dict,
    strategy: str = "default",
    config: Optional[Config] = None,
) -> list:
    cfg = config or Config()
    strat = get_strategy(strategy)
    return [user for user in users if strat.matches(user, criteria, cfg)]
