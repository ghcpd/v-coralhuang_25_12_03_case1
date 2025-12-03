import json
from typing import Iterable, Mapping, Any, Sequence, Optional, List, Tuple

DEFAULT_FIELDS: Tuple[str, ...] = (
    "id",
    "name",
    "email",
    "role",
    "status",
    "join_date",
    "last_login",
)


def select_fields(
    user: Mapping[str, Any],
    include: Optional[Sequence[str]] = None,
    exclude: Optional[Sequence[str]] = None,
    default_fields: Sequence[str] = DEFAULT_FIELDS,
) -> Mapping[str, Any]:
    if include:
        fields = list(include)
    else:
        fields = list(default_fields)
    if exclude:
        fields = [f for f in fields if f not in exclude]
    return {f: user.get(f, "<missing>") for f in fields}


def _format_key(k: Any, upper_id: bool = False) -> Any:
    if not isinstance(k, str):
        return k
    if upper_id and k.lower() == "id":
        return "ID"
    return k.title()


def format_user(
    user: Mapping[str, Any],
    mode: str = "compact",
    include: Optional[Sequence[str]] = None,
    exclude: Optional[Sequence[str]] = None,
) -> str:
    data = select_fields(user, include, exclude)
    if mode == "compact":
        parts = [f"{_format_key(k, upper_id=True)}: {v}" for k, v in data.items()]
        return " | ".join(parts)
    elif mode == "verbose":
        lines = [f"{_format_key(k)}: {v}" for k, v in data.items()]
        return "\n".join(lines)
    elif mode == "json":
        return json.dumps(data, ensure_ascii=False)
    else:
        raise ValueError(f"Unknown formatter mode: {mode}")


def format_users(
    users: Iterable[Mapping[str, Any]],
    mode: str = "compact",
    include: Optional[Sequence[str]] = None,
    exclude: Optional[Sequence[str]] = None,
    show_total: bool = False,
) -> str:
    user_list = list(users)
    lines: List[str] = [format_user(u, mode=mode, include=include, exclude=exclude) for u in user_list]
    if show_total:
        lines.append("")
        lines.append(f"Total users processed: {len(user_list)}")
    return "\n".join(lines)
