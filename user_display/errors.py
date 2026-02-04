"""Custom exceptions for user_display."""


class UserValidationError(Exception):
    """Raised when a user record fails validation but we want graceful recovery."""

    def __init__(self, message: str, user=None):
        super().__init__(message)
        self.user = user
