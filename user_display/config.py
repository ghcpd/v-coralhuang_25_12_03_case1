from dataclasses import dataclass, replace
from typing import Optional, Sequence, Callable, Mapping, Any, Tuple

DEFAULT_REQUIRED_FIELDS: Tuple[str, ...] = (
    "id",
    "name",
    "email",
    "role",
    "status",
    "join_date",
    "last_login",
)


def default_validator(user: Mapping[str, Any], required_fields: Tuple[str, ...] = DEFAULT_REQUIRED_FIELDS):
    missing = [k for k in required_fields if k not in user]
    return len(missing) == 0, missing


@dataclass(frozen=True)
class Config:
    default_formatter: str = "compact"
    case_insensitive: bool = True
    enable_filter_cache: bool = True
    max_cache_size: int = 128
    required_fields: Tuple[str, ...] = DEFAULT_REQUIRED_FIELDS
    include_fields: Optional[Sequence[str]] = None
    exclude_fields: Optional[Sequence[str]] = None
    validation_strategy: Optional[Callable[[Mapping[str, Any]], Any]] = None


DEFAULT_CONFIG = Config()


def get_config(overrides: Optional[Mapping[str, Any]] = None, base: Optional[Config] = None) -> Config:
    cfg = base or DEFAULT_CONFIG
    if overrides is None:
        return cfg
    return replace(cfg, **overrides)
