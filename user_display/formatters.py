"""Formatting helpers for user display.

Support compact, verbose and json-ish formatting. Use join to avoid
repeated concatenation and allow include/exclude of fields.
"""
from typing import Dict, Iterable, List, Optional
import json

DEFAULT_FIELDS = [
    "id",
    "name",
    "email",
    "role",
    "status",
    "join_date",
    "last_login",
]


def _safe_get(user: Dict, field: str):
    # gracefully handle missing values
    val = user.get(field, "")
    return "" if val is None else str(val)


def format_user(user: Dict, mode: str = "compact", include: Optional[List[str]] = None, exclude: Optional[List[str]] = None) -> str:
    include_set = set(include) if include else set(DEFAULT_FIELDS)
    if exclude:
        include_set -= set(exclude)

    fields = [f for f in DEFAULT_FIELDS if f in include_set]

    if mode == "compact":
        parts = []
        if "id" in fields:
            parts.append(f"ID: {_safe_get(user, 'id')}")
        if "name" in fields:
            parts.append(f"Name: {_safe_get(user, 'name')}")
        if "email" in fields:
            parts.append(f"Email: {_safe_get(user, 'email')}")

        # append remaining fields succinctly
        parts += [f"{k.replace('_',' ').title()}: {_safe_get(user,k)}" for k in fields if k not in ("id","name","email")]
        return " | ".join(parts)

    if mode == "verbose":
        lines = [f"User ID: {_safe_get(user, 'id')}" ]
        for k in fields:
            lines.append(f"  {k.replace('_',' ').title()}: {_safe_get(user,k)}")
        return "\n".join(lines)

    if mode == "json":
        obj = {k: user.get(k, None) for k in fields}
        return json.dumps(obj, default=str)

    raise ValueError("Unsupported mode: %s" % mode)


def format_users(users: Iterable[Dict], mode: str = "compact", include=None, exclude=None, show_all=True) -> str:
    lines = [format_user(u, mode=mode, include=include, exclude=exclude) for u in users]
    out = "\n".join(lines)
    if show_all:
        out = out + "\n\nTotal users processed: " + str(len(lines))
    return out
