"""Configuration management for the user display module."""

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Config:
    """
    Configuration for user display operations.

    This class centralizes all configurable behavior to avoid
    hard-coded values throughout the codebase.
    """

    # Formatter settings
    default_formatter: str = "compact"  # compact, verbose, json_like
    default_fields: Optional[List[str]] = None  # None means all fields
    field_separator: str = " | "
    line_separator: str = "\n"

    # Filter settings
    case_sensitive: bool = False
    enable_cache: bool = True
    cache_max_size: int = 100

    # Validation settings
    required_fields: List[str] = field(
        default_factory=lambda: ["id", "name", "email", "role", "status"]
    )
    strict_validation: bool = False  # If True, reject invalid records
    auto_fix_malformed: bool = True  # Try to fix malformed records

    # Performance settings
    max_batch_size: int = 10000
    enable_metrics: bool = True

    # Display settings
    show_total_count: bool = True
    verbose_logging: bool = False

    # Export settings
    export_separator: str = "=" * 80
    export_item_separator: str = "-" * 80

    @classmethod
    def default(cls) -> "Config":
        """Create a default configuration instance."""
        return cls()

    @classmethod
    def high_performance(cls) -> "Config":
        """Create a high-performance configuration."""
        return cls(
            enable_cache=True,
            strict_validation=False,
            enable_metrics=False,
            verbose_logging=False,
        )

    @classmethod
    def strict(cls) -> "Config":
        """Create a strict configuration with validation."""
        return cls(
            strict_validation=True,
            auto_fix_malformed=False,
            verbose_logging=True,
        )


# Global default configuration
default_config = Config.default()
