"""Output formatters for user display."""

from typing import List, Dict, Any, Optional, Set
from .config import get_config


class Formatter:
    """Base formatter interface."""

    def format_users(self, users: List[Dict[str, Any]]) -> str:
        """Format a list of users to string."""
        raise NotImplementedError

    def format_user(self, user: Dict[str, Any]) -> str:
        """Format a single user to string."""
        raise NotImplementedError

    def _apply_field_filter(self, user: Dict[str, Any]) -> Dict[str, Any]:
        """Apply include/exclude field filtering."""
        config = get_config()

        if config.include_fields:
            filtered = {k: v for k, v in user.items() if k in config.include_fields}
        else:
            filtered = dict(user)

        for field in config.exclude_fields:
            filtered.pop(field, None)

        return filtered


class CompactFormatter(Formatter):
    """Compact single-line format."""

    def format_users(self, users: List[Dict[str, Any]]) -> str:
        """Format users in compact form."""
        lines = [self.format_user(user) for user in users]
        if lines:
            lines.append(f"\nTotal users: {len(users)}")
        return "\n".join(lines)

    def format_user(self, user: Dict[str, Any]) -> str:
        """Format single user in compact form."""
        filtered = self._apply_field_filter(user)
        parts = [f"{k}={v}" for k, v in filtered.items()]
        return " | ".join(parts)


class VerboseFormatter(Formatter):
    """Multi-line verbose format."""

    def format_users(self, users: List[Dict[str, Any]]) -> str:
        """Format users in verbose form."""
        lines = []
        for user in users:
            lines.append(self.format_user(user))
        if lines:
            lines.append(f"\n--- Total users: {len(users)} ---")
        return "\n".join(lines)

    def format_user(self, user: Dict[str, Any]) -> str:
        """Format single user in verbose form."""
        filtered = self._apply_field_filter(user)
        lines = []
        for key, value in filtered.items():
            lines.append(f"  {key}: {value}")
        return "User:\n" + "\n".join(lines) + "\n" + "-" * 40


class JSONLikeFormatter(Formatter):
    """JSON-like format (not strict JSON for compatibility)."""

    def format_users(self, users: List[Dict[str, Any]]) -> str:
        """Format users in JSON-like form."""
        lines = ["["]
        for i, user in enumerate(users):
            filtered = self._apply_field_filter(user)
            user_str = self._dict_to_json_like(filtered)
            if i < len(users) - 1:
                lines.append(user_str + ",")
            else:
                lines.append(user_str)
        lines.append("]")
        return "\n".join(lines)

    def format_user(self, user: Dict[str, Any]) -> str:
        """Format single user in JSON-like form."""
        filtered = self._apply_field_filter(user)
        return self._dict_to_json_like(filtered)

    def _dict_to_json_like(self, d: Dict[str, Any]) -> str:
        """Convert dict to JSON-like string."""
        items = []
        for k, v in d.items():
            if isinstance(v, str):
                items.append(f'  "{k}": "{v}"')
            else:
                items.append(f'  "{k}": {v}')
        return "{\n" + ",\n".join(items) + "\n}"


class ExportFormatter(Formatter):
    """Export format with headers and separators."""

    def format_users(self, users: List[Dict[str, Any]]) -> str:
        """Format users in export form."""
        lines = ["USER_EXPORT_START", "=" * 80]

        for user in users:
            lines.append(self.format_user(user))

        lines.append("USER_EXPORT_END")
        return "\n".join(lines)

    def format_user(self, user: Dict[str, Any]) -> str:
        """Format single user in export form."""
        filtered = self._apply_field_filter(user)
        lines = []
        for key, value in filtered.items():
            lines.append(f"  {key}: {value}")
        lines.append("-" * 80)
        return "\n".join(lines)


def get_formatter(formatter_type: str = "compact") -> Formatter:
    """Get a formatter by type."""
    formatters = {
        "compact": CompactFormatter(),
        "verbose": VerboseFormatter(),
        "json": JSONLikeFormatter(),
        "export": ExportFormatter(),
    }
    return formatters.get(formatter_type.lower(), CompactFormatter())
