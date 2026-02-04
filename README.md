# User Display Module — Optimized & Modular

## Overview

This project refactors the baseline `input.py` (now `user_display_original.py`) into a high-performance, modular, and extensible system while preserving the original public API via `user_display_optimized.py`.

## Baseline Issues

- O(n²) string concatenation; artificial `time.sleep`
- Linear ID lookups; no indexing
- Monolithic design; no separation of concerns
- No validation, logging, or resilience to malformed records
- Fixed formatting & filtering logic; no extensibility

## New Architecture

```
user_display/
    __init__.py
    store.py          # UserStore: indexing, filtering, snapshotting, thread-safe reads, caching
    formatters.py     # compact / verbose / export / JSON; include/exclude fields
    filters.py        # pluggable strategies; default multi-criteria with case control
    config.py         # defaults for formatter, case rules, caching, validation
    logging_utils.py  # unified logger with [MARKER]
    metrics.py        # thread-safe counters
    errors.py         # custom exceptions
    validators.py     # pluggable validation logic
```

## Key Features

- **Performance**: O(1) ID lookup; buffered joins; no sleeps; efficient for 1k–10k users
- **Formatting**: `compact` (baseline-compatible), `verbose`, `export` (baseline-compatible), `json`
- **Field Selection**: include/exclude fields per call
- **Filtering**: strategy-based; case sensitivity control; optional caching
- **Validation**: pluggable; graceful skipping of malformed records with metrics/logging
- **Concurrency**: reader-writer lock for thread-safe reads; snapshot/clone support
- **Metrics & Logging**: counters for operations/cache; `[MARKER]`-prefixed logs

## API Compatibility

`user_display_optimized.py` exposes the same functions as the baseline:

- `display_users(users, show_all=True, verbose=False, *, formatter=None, include_fields=None, exclude_fields=None, ...)`
- `get_user_by_id(users, user_id, ...)`
- `filter_users(users, criteria, *, strategy='default', case_sensitive=None, use_cache=None, ...)`
- `export_users_to_string(users, ...)`

Defaults produce output identical to the baseline.

## Usage Examples

```python
from user_display_optimized import display_users, filter_users

# Compact (baseline) formatting
print(display_users(users))

# JSON formatting with selected fields
print(display_users(users, formatter="json", include_fields=["id", "email"]))

# Case-sensitive filtering with caching disabled
active_admins = filter_users(users, {"role": "Admin", "status": "Active"}, case_sensitive=True, use_cache=False)
```

## Performance Targets (sanity checks)

| Operation       | Target    |
|----------------|-----------|
| Display 1,000   | < 100 ms  |
| Filter 1,000    | < 10 ms   |
| Lookup by ID    | < 1 ms    |

Tests include generous thresholds to avoid flakiness but the implementation typically meets or beats targets on commodity hardware.

## Tests

- Functional, robustness, concurrency, and performance tests in `tests/`
- Run all tests via `run_tests.ps1` (Windows) or `python run_tests.py`

## Quick Start

```powershell
# Windows
./run_tests.ps1
```

```bash
# Cross-platform
python run_tests.py
```

## Notes

- Dependencies are minimal: see `requirements.txt` (pinned `pytest`).
- The baseline `user_display_original.py` is preserved for reference and compatibility testing.
