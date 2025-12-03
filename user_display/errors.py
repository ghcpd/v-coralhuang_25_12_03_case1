class UserDisplayError(Exception):
    """Base exception for user display errors."""


class ValidationError(UserDisplayError):
    """Raised when validation fails."""


class UserNotFoundError(UserDisplayError):
    """Raised when a user cannot be found."""
