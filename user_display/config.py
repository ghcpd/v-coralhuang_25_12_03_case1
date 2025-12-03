from dataclasses import dataclass, field
from typing import Iterable, Optional, Sequence, Set

DEFAULT_FIELDS: Sequence[str] = (
    "id",
    "name",
    "email",
    "role",
    "status",
    "join_date",
    "last_login",
)


@dataclass
class Config:
    default_formatter: str = "compact"
    include_fields: Optional[Iterable[str]] = None
    exclude_fields: Optional[Iterable[str]] = None
    case_sensitive: bool = False
    enable_filter_cache: bool = True
    logging_marker: str = "[MARKER]"
    validation_required_id: bool = True
    validation_required_fields: Set[str] = field(default_factory=set)  # optional additional required fields

    def normalized_include(self) -> Optional[Sequence[str]]:
        return tuple(self.include_fields) if self.include_fields is not None else None

    def normalized_exclude(self) -> Optional[Sequence[str]]:
        return tuple(self.exclude_fields) if self.exclude_fields is not None else None


def default_config() -> "Config":
    return Config()
