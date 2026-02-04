"""Custom exceptions for user display module."""


class UserDisplayError(Exception):
    """Base exception for user display module."""
    pass


class UserNotFoundError(UserDisplayError):
    """Raised when a user is not found."""
    pass


class InvalidUserDataError(UserDisplayError):
    """Raised when user data is invalid or malformed."""
    pass


class ValidationError(UserDisplayError):
    """Raised when validation fails."""
    pass
