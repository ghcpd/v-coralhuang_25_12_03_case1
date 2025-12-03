"""Pluggable formatters for different output styles."""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional

from .config import Config
from .metrics import global_metrics


class BaseFormatter(ABC):
    """Base class for all formatters."""

    def __init__(self, config: Optional[Config] = None):
        """
        Initialize the formatter.

        Args:
            config: Configuration instance
        """
        self._config = config or Config.default()

    @abstractmethod
    def format_user(self, user: Dict[str, Any]) -> str:
        """
        Format a single user record.

        Args:
            user: User dictionary

        Returns:
            Formatted string
        """
        pass

    def format_users(
        self,
        users: List[Dict[str, Any]],
        show_total: bool = True,
        fields: Optional[List[str]] = None,
    ) -> str:
        """
        Format multiple users efficiently using join.

        Args:
            users: List of user dictionaries
            show_total: Whether to append total count
            fields: Optional list of fields to include

        Returns:
            Formatted string with all users
        """
        if self._config.enable_metrics:
            global_metrics.increment("formatter.format_users")

        # Store fields for use in format_user
        self._selected_fields = fields

        # Efficiently build result using join
        lines = [self.format_user(user) for user in users]

        if show_total and self._config.show_total_count:
            lines.append(f"\nTotal users processed: {len(users)}\n")

        return "".join(lines)

    def _get_field_value(self, user: Dict[str, Any], field: str) -> str:
        """
        Get field value with safe fallback.

        Args:
            user: User dictionary
            field: Field name

        Returns:
            Field value as string or 'N/A' if missing
        """
        return str(user.get(field, "N/A"))

    def _filter_fields(self, user: Dict[str, Any]) -> Dict[str, Any]:
        """
        Filter user to selected fields if specified.

        Args:
            user: User dictionary

        Returns:
            Filtered user dictionary
        """
        if hasattr(self, "_selected_fields") and self._selected_fields:
            return {k: v for k, v in user.items() if k in self._selected_fields}
        return user


class CompactFormatter(BaseFormatter):
    """
    Compact single-line formatter.

    Output format: ID: 1 | Name: John | Email: john@example.com | ...
    """

    def format_user(self, user: Dict[str, Any]) -> str:
        """Format user in compact single-line style."""
        filtered_user = self._filter_fields(user)

        parts = []
        for key, value in filtered_user.items():
            # Capitalize field names for display
            display_key = key.replace("_", " ").title()
            parts.append(f"{display_key}: {value}")

        separator = self._config.field_separator
        return separator.join(parts) + "\n"


class VerboseFormatter(BaseFormatter):
    """
    Verbose multi-line formatter with indentation.

    Output format:
    User ID: 1
      Name: John Doe
      Email: john@example.com
      ...
    """

    def format_user(self, user: Dict[str, Any]) -> str:
        """Format user in verbose multi-line style."""
        filtered_user = self._filter_fields(user)

        lines = []
        first = True
        for key, value in filtered_user.items():
            display_key = key.replace("_", " ").title()
            if first and key == "id":
                lines.append(f"User ID: {value}")
                first = False
            else:
                lines.append(f"  {display_key}: {value}")

        lines.append(self._config.export_item_separator)
        return "\n".join(lines) + "\n"


class JSONLikeFormatter(BaseFormatter):
    """
    JSON-like formatter (not valid JSON, but similar structure).

    Output format:
    {
      "id": 1,
      "name": "John Doe",
      ...
    }
    """

    def format_user(self, user: Dict[str, Any]) -> str:
        """Format user in JSON-like style."""
        filtered_user = self._filter_fields(user)

        lines = ["{"]
        items = list(filtered_user.items())
        for idx, (key, value) in enumerate(items):
            # Add quotes around strings
            if isinstance(value, str):
                value_str = f'"{value}"'
            else:
                value_str = str(value)

            comma = "," if idx < len(items) - 1 else ""
            lines.append(f'  "{key}": {value_str}{comma}')

        lines.append("}")
        return "\n".join(lines) + "\n"


class TableFormatter(BaseFormatter):
    """
    Table-style formatter with aligned columns.

    Output format:
    | ID | Name      | Email               | ...
    |----|-----------|---------------------|
    | 1  | John Doe  | john@example.com    | ...
    """

    def __init__(self, config: Optional[Config] = None):
        super().__init__(config)
        self._column_widths = {}

    def _calculate_column_widths(
        self, users: List[Dict[str, Any]], fields: Optional[List[str]] = None
    ) -> Dict[str, int]:
        """Calculate optimal column widths for alignment."""
        if not users:
            return {}

        # Determine fields to display
        if fields:
            display_fields = fields
        else:
            display_fields = list(users[0].keys())

        widths = {}
        for field in display_fields:
            # Start with field name width
            max_width = len(field.replace("_", " ").title())

            # Check all user values
            for user in users:
                value_width = len(str(user.get(field, "N/A")))
                max_width = max(max_width, value_width)

            widths[field] = max_width + 2  # Add padding

        return widths

    def format_users(
        self,
        users: List[Dict[str, Any]],
        show_total: bool = True,
        fields: Optional[List[str]] = None,
    ) -> str:
        """Format users as aligned table."""
        if not users:
            return "No users to display\n"

        self._selected_fields = fields
        self._column_widths = self._calculate_column_widths(users, fields)

        # Determine fields
        if fields:
            display_fields = fields
        else:
            display_fields = list(users[0].keys())

        lines = []

        # Header row
        header_parts = []
        for field in display_fields:
            display_name = field.replace("_", " ").title()
            width = self._column_widths[field]
            header_parts.append(display_name.ljust(width))
        lines.append("| " + " | ".join(header_parts) + " |")

        # Separator row
        separator_parts = ["-" * self._column_widths[field] for field in display_fields]
        lines.append("|-" + "-|-".join(separator_parts) + "-|")

        # Data rows
        for user in users:
            row_parts = []
            for field in display_fields:
                value = str(user.get(field, "N/A"))
                width = self._column_widths[field]
                row_parts.append(value.ljust(width))
            lines.append("| " + " | ".join(row_parts) + " |")

        if show_total and self._config.show_total_count:
            lines.append(f"\nTotal users: {len(users)}\n")

        return "\n".join(lines) + "\n"

    def format_user(self, user: Dict[str, Any]) -> str:
        """Format single user (not optimal for table format)."""
        # For single user, fall back to compact format
        compact = CompactFormatter(self._config)
        return compact.format_user(user)


def get_formatter(name: str, config: Optional[Config] = None) -> BaseFormatter:
    """
    Factory function to get formatter by name.

    Args:
        name: Formatter name (compact, verbose, json_like, table)
        config: Configuration instance

    Returns:
        Formatter instance
    """
    formatters = {
        "compact": CompactFormatter,
        "verbose": VerboseFormatter,
        "json_like": JSONLikeFormatter,
        "table": TableFormatter,
    }

    formatter_class = formatters.get(name.lower())
    if formatter_class is None:
        # Default to compact
        formatter_class = CompactFormatter

    return formatter_class(config)
