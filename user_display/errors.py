class UserDisplayError(Exception):
    """Base error for user display module."""


class ValidationError(UserDisplayError):
    """Raised when a user record fails validation."""


class NotFoundError(UserDisplayError):
    """Raised when a user is not found."""
