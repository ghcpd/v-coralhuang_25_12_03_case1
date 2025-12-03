"""Output formatters for user display."""

import json
from .errors import MalformedUserError
from .logging_utils import get_logger

logger = get_logger()


class Formatter:
    """Base formatter class."""

    def format_user(self, user, fields=None):
        """Format a single user. Must be overridden by subclasses."""
        raise NotImplementedError

    def format_users(self, users, fields=None):
        """Format multiple users."""
        raise NotImplementedError

    def _validate_user(self, user):
        """Validate user has required fields, skip missing ones gracefully."""
        if not isinstance(user, dict):
            raise MalformedUserError(f"User must be a dict, got {type(user)}")
        return user

    def _safe_get(self, user, field, default="N/A"):
        """Safely get a field from user, return default if missing."""
        try:
            return str(user.get(field, default))
        except (AttributeError, TypeError):
            logger.warning(f"Could not extract field '{field}' from user {user.get('id', 'unknown')}")
            return default


class CompactFormatter(Formatter):
    """Compact single-line format."""

    def format_user(self, user, fields=None):
        """Format a single user in compact form."""
        user = self._validate_user(user)
        user_id = self._safe_get(user, "id")
        name = self._safe_get(user, "name")
        email = self._safe_get(user, "email")
        role = self._safe_get(user, "role")
        status = self._safe_get(user, "status")
        join_date = self._safe_get(user, "join_date")
        last_login = self._safe_get(user, "last_login")

        return (
            f"ID: {user_id} | Name: {name} | Email: {email} | "
            f"Role: {role} | Status: {status} | Join Date: {join_date} | Last Login: {last_login}"
        )

    def format_users(self, users, fields=None):
        """Format multiple users in compact form."""
        lines = []
        for user in users:
            try:
                lines.append(self.format_user(user, fields))
            except MalformedUserError as e:
                logger.warning(f"Skipping malformed user: {e}")
                continue
        return "\n".join(lines)


class VerboseFormatter(Formatter):
    """Verbose multi-line format."""

    def format_user(self, user, fields=None):
        """Format a single user in verbose form."""
        user = self._validate_user(user)
        user_id = self._safe_get(user, "id")
        name = self._safe_get(user, "name")
        email = self._safe_get(user, "email")
        role = self._safe_get(user, "role")
        status = self._safe_get(user, "status")
        join_date = self._safe_get(user, "join_date")
        last_login = self._safe_get(user, "last_login")

        return (
            f"User ID: {user_id}\n"
            f"  Name: {name}\n"
            f"  Email: {email}\n"
            f"  Role: {role}\n"
            f"  Status: {status}\n"
            f"  Join Date: {join_date}\n"
            f"  Last Login: {last_login}"
        )

    def format_users(self, users, fields=None):
        """Format multiple users in verbose form."""
        lines = []
        lines.append("=" * 80)
        for user in users:
            try:
                lines.append(self.format_user(user, fields))
                lines.append("-" * 80)
            except MalformedUserError as e:
                logger.warning(f"Skipping malformed user: {e}")
                continue
        return "\n".join(lines)


class JSONFormatter(Formatter):
    """JSON output format."""

    def format_user(self, user, fields=None):
        """Format a single user as JSON."""
        user = self._validate_user(user)
        return json.dumps(user, indent=2)

    def format_users(self, users, fields=None):
        """Format multiple users as JSON array."""
        valid_users = []
        for user in users:
            try:
                self._validate_user(user)
                valid_users.append(user)
            except MalformedUserError as e:
                logger.warning(f"Skipping malformed user: {e}")
                continue
        return json.dumps(valid_users, indent=2)


class ExportFormatter(Formatter):
    """Export format with headers and separators."""

    def format_users(self, users, fields=None):
        """Format multiple users for export."""
        lines = []
        lines.append("USER_EXPORT_START")
        lines.append("=" * 80)

        for user in users:
            try:
                user = self._validate_user(user)
                user_id = self._safe_get(user, "id")
                name = self._safe_get(user, "name")
                email = self._safe_get(user, "email")
                role = self._safe_get(user, "role")
                status = self._safe_get(user, "status")
                join_date = self._safe_get(user, "join_date")
                last_login = self._safe_get(user, "last_login")

                lines.append(f"User ID: {user_id}")
                lines.append(f"  Name: {name}")
                lines.append(f"  Email: {email}")
                lines.append(f"  Role: {role}")
                lines.append(f"  Status: {status}")
                lines.append(f"  Join Date: {join_date}")
                lines.append(f"  Last Login: {last_login}")
                lines.append("-" * 80)
            except MalformedUserError as e:
                logger.warning(f"Skipping malformed user: {e}")
                continue

        lines.append("USER_EXPORT_END")
        return "\n".join(lines)

    def format_user(self, user, fields=None):
        """Not implemented for export formatter."""
        raise NotImplementedError("ExportFormatter only supports format_users()")


def get_formatter(formatter_type):
    """Get a formatter by type."""
    formatters = {
        "compact": CompactFormatter,
        "verbose": VerboseFormatter,
        "json": JSONFormatter,
        "export": ExportFormatter,
    }
    formatter_class = formatters.get(formatter_type, CompactFormatter)
    return formatter_class()
