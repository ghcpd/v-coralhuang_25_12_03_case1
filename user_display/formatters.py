import json
from typing import Dict, Iterable, Optional, Sequence
from .config import DEFAULT_FIELDS

_PLACEHOLDER = "N/A"


def _safe_user_fields(user: dict, include_fields: Optional[Sequence[str]], exclude_fields: Optional[Sequence[str]]):
    # Determine fields to use preserving DEFAULT_FIELDS order
    if include_fields is None:
        fields = list(DEFAULT_FIELDS)
    else:
        fields = list(include_fields)
    if exclude_fields:
        fields = [f for f in fields if f not in exclude_fields]
    return {field: user.get(field, _PLACEHOLDER) for field in fields}


class BaseFormatter:
    name: str = "base"

    def format_user(self, user: dict, include_fields=None, exclude_fields=None) -> str:
        raise NotImplementedError

    def format_many(self, users: Iterable[dict], include_fields=None, exclude_fields=None, show_all: bool = False) -> str:
        # Default implementation joins per-user formatting
        lines = [self.format_user(u, include_fields, exclude_fields) for u in users]
        return "\n".join(lines)


class CompactFormatter(BaseFormatter):
    name = "compact"

    def format_user(self, user: dict, include_fields=None, exclude_fields=None) -> str:
        fields = _safe_user_fields(user, include_fields, exclude_fields)
        parts = []
        for key in fields:
            label = "ID" if key == "id" else key.replace("_", " ").title()
            parts.append(f"{label}: {fields[key]}")
        return " | ".join(parts)


class VerboseFormatter(BaseFormatter):
    name = "verbose"

    def format_user(self, user: dict, include_fields=None, exclude_fields=None) -> str:
        fields = _safe_user_fields(user, include_fields, exclude_fields)
        lines = []
        for k, v in fields.items():
            label = "ID" if k == "id" else k.replace("_", " ").title()
            lines.append(f"{label}: {v}")
        return "\n".join(lines)

    def format_many(self, users: Iterable[dict], include_fields=None, exclude_fields=None, show_all: bool = False) -> str:
        chunks = []
        for user in users:
            chunks.append(self.format_user(user, include_fields, exclude_fields))
            chunks.append("-" * 80)
        if chunks:
            chunks.pop()  # remove last separator
        return "\n".join(chunks)


class ExportFormatter(BaseFormatter):
    name = "export"

    def format_many(self, users: Iterable[dict], include_fields=None, exclude_fields=None, show_all: bool = False) -> str:
        lines = ["USER_EXPORT_START", "=" * 80]
        for user in users:
            fields = _safe_user_fields(user, include_fields, exclude_fields)
            for idx, (k, v) in enumerate(fields.items()):
                if k == "id":
                    lines.append(f"User ID: {v}")
                else:
                    label = k.replace("_", " ").title()
                    lines.append(f"  {label}: {v}")
            lines.append("-" * 80)
        lines.append("USER_EXPORT_END")
        return "\n".join(lines) + "\n"


class JsonFormatter(BaseFormatter):
    name = "json"

    def format_many(self, users: Iterable[dict], include_fields=None, exclude_fields=None, show_all: bool = False) -> str:
        arr = []
        for user in users:
            arr.append(_safe_user_fields(user, include_fields, exclude_fields))
        return json.dumps(arr, indent=2)


_formatters: Dict[str, BaseFormatter] = {
    CompactFormatter.name: CompactFormatter(),
    VerboseFormatter.name: VerboseFormatter(),
    ExportFormatter.name: ExportFormatter(),
    JsonFormatter.name: JsonFormatter(),
}


def register_formatter(name: str, formatter: BaseFormatter) -> None:
    _formatters[name] = formatter


def get_formatter(name: str) -> BaseFormatter:
    return _formatters.get(name, _formatters[CompactFormatter.name])


def format_users(
    users: Iterable[dict],
    formatter: str = "compact",
    include_fields: Optional[Sequence[str]] = None,
    exclude_fields: Optional[Sequence[str]] = None,
    show_all: bool = False,
) -> str:
    fmt = get_formatter(formatter)
    return fmt.format_many(users, include_fields, exclude_fields, show_all)
