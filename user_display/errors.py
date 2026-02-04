class ValidationError(Exception):
    """Raised when input validation fails."""


class MissingFieldError(ValidationError):
    """Raised when a required field is missing from a user record."""
