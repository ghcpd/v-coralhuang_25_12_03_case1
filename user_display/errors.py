"""Custom exception classes for the user display module."""


class UserDisplayError(Exception):
    """Base exception for all user display module errors."""

    pass


class ValidationError(UserDisplayError):
    """Raised when user data validation fails."""

    pass


class UserNotFoundError(UserDisplayError):
    """Raised when a requested user cannot be found."""

    pass


class FilterError(UserDisplayError):
    """Raised when a filter operation fails."""

    pass


class FormatterError(UserDisplayError):
    """Raised when a formatting operation fails."""

    pass
