from typing import Any, Iterable, List, Mapping, Optional

try:  # Python <3.8
    from typing import Protocol
except ImportError:  # pragma: no cover
    from typing_extensions import Protocol  # type: ignore


class FilterStrategy(Protocol):
    name: str

    def filter(
        self,
        users: Iterable[Mapping[str, Any]],
        criteria: Mapping[str, Any],
        case_insensitive: bool = True,
    ) -> List[Mapping[str, Any]]:
        ...


def _string_match(user_val: str, crit_val: str, case_insensitive: bool, contains: bool) -> bool:
    if case_insensitive:
        user_val = user_val.lower()
        crit_val = crit_val.lower()
    return crit_val in user_val if contains else user_val == crit_val


def _matches(user: Mapping[str, Any], criteria: Mapping[str, Any], case_insensitive: bool) -> bool:
    for key, crit_val in criteria.items():
        user_val = user.get(key)
        if user_val is None:
            return False
        if isinstance(user_val, str) and isinstance(crit_val, str):
            contains = key in {"name", "email"}
            if not _string_match(user_val, crit_val, case_insensitive, contains):
                return False
        else:
            if user_val != crit_val:
                return False
    return True


class SimpleCriteriaFilter:
    name = "simple"

    def filter(
        self,
        users: Iterable[Mapping[str, Any]],
        criteria: Mapping[str, Any],
        case_insensitive: bool = True,
    ) -> List[Mapping[str, Any]]:
        return [u for u in users if _matches(u, criteria, case_insensitive)]




def filter_users(
    users: Iterable[Mapping[str, Any]],
    criteria: Mapping[str, Any],
    case_insensitive: bool = True,
    strategy: Optional[FilterStrategy] = None,
) -> List[Mapping[str, Any]]:
    strat = strategy or SimpleCriteriaFilter()
    return strat.filter(users, criteria, case_insensitive)
