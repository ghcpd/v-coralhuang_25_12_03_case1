"""Custom exceptions for the user_display module."""


class UserDisplayError(Exception):
    """Base exception for user_display module."""
    pass


class MalformedUserError(UserDisplayError):
    """Raised when a user record has missing or invalid fields."""
    pass


class ValidationError(UserDisplayError):
    """Raised when validation of user data fails."""
    pass


class FilterError(UserDisplayError):
    """Raised when filter application fails."""
    pass
