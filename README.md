# User Display — optimized, modular, extensible

This repository contains a refactor of a deliberately naive `input.py` baseline implementation into a modular and high-performance `user_display` package.

## Highlights
- Preserves the original public API via `user_display_optimized.py` functions:
  - `display_users(...)`, `get_user_by_id(...)`, `filter_users(...)`, `export_users_to_string(...)`
- New package layout (modular):

```
user_display/
    __init__.py
    store.py
    formatters.py
    filters.py
    config.py
    logging_utils.py
    metrics.py
    errors.py
user_display_original.py  (baseline copy)
user_display_optimized.py (compatibility wrapper)
```

## Improvements
- Performance: O(1) lookups via index map, efficient formatting with join, no artificial sleeps.
- Reliability: graceful handling of malformed records, validation hook, centralized logging with `[MARKER]`.
- Extensibility: pluggable filters, formatters, caching and metrics.

## Usage examples
From Python:

```py
from user_display_optimized import display_users, get_user_by_id

text = display_users(users)
user = get_user_by_id(users, 3)
```

## Tests
Run tests via the provided run_tests.ps1 or with pytest directly:

PowerShell:

```powershell
./run_tests.ps1
```

Or with pytest:

```powershell
python -m pip install -r requirements.txt
pytest -q
```

## Performance targets (sanity checks included in tests)
| Operation     | Target  |
| ------------- | ------- |
| Display 1,000 | < 100ms |
| Filter 1,000  | < 10ms  |
| Lookup by ID  | < 1ms   |
