"""Configuration and defaults for the user_display module."""


class Config:
    """Global configuration for user_display module."""

    # Formatter settings
    DEFAULT_FORMATTER = "compact"
    AVAILABLE_FORMATTERS = ("compact", "verbose", "json")

    # Filter settings
    CASE_SENSITIVE_FILTERS = False
    ENABLE_FILTER_CACHING = True
    MAX_CACHE_ENTRIES = 100

    # Logging settings
    LOG_MARKER = "[USER_DISPLAY]"
    ENABLE_LOGGING = True

    # Metrics settings
    ENABLE_METRICS = True

    # Field settings
    REQUIRED_FIELDS = {"id", "name", "email", "role", "status", "join_date", "last_login"}
    OPTIONAL_FIELDS = set()

    # Performance settings
    ENABLE_INDEXING = True
    SNAPSHOT_ON_MODIFICATION = False

    @classmethod
    def get_default_fields(cls):
        """Get the set of fields to display by default."""
        return cls.REQUIRED_FIELDS.copy()

    @classmethod
    def update(cls, **kwargs):
        """Update configuration settings."""
        for key, value in kwargs.items():
            if hasattr(cls, key):
                setattr(cls, key, value)
