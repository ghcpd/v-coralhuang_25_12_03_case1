"""Configuration management for user display module."""

from typing import Dict, Any, Optional


class Config:
    """Configuration object for user display behavior."""

    def __init__(self):
        # Formatter settings
        self.default_formatter = "compact"
        self.include_fields = None  # None = all fields
        self.exclude_fields = []

        # Filter settings
        self.case_sensitive_filters = False
        self.enable_filter_cache = True
        self.cache_max_size = 100

        # Behavior settings
        self.skip_malformed_records = True
        self.validate_on_insert = True
        self.verbose_logging = False

        # Performance settings
        self.build_index = True
        self.thread_safe = True

    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary."""
        return {
            "default_formatter": self.default_formatter,
            "include_fields": self.include_fields,
            "exclude_fields": self.exclude_fields,
            "case_sensitive_filters": self.case_sensitive_filters,
            "enable_filter_cache": self.enable_filter_cache,
            "cache_max_size": self.cache_max_size,
            "skip_malformed_records": self.skip_malformed_records,
            "validate_on_insert": self.validate_on_insert,
            "verbose_logging": self.verbose_logging,
            "build_index": self.build_index,
            "thread_safe": self.thread_safe,
        }

    @staticmethod
    def default() -> "Config":
        """Get default configuration."""
        return Config()


# Global config instance
_config = Config()


def get_config() -> Config:
    """Get the global config instance."""
    return _config


def set_config(config: Config) -> None:
    """Set the global config instance."""
    global _config
    _config = config


def reset_config() -> None:
    """Reset to default configuration."""
    global _config
    _config = Config()
