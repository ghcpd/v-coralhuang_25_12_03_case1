# User Display Module — Optimized

## Baseline Issues
- O(n²) string concatenation, artificial delays
- Linear lookup, no indexing
- Monolithic single file, no separation of concerns
- No validation/logging/metrics; crashes on malformed data
- Hard-coded formatting and filtering

## New Architecture
```
user_display/
  __init__.py
  config.py          # defaults, validation
  logging_utils.py   # unified `[MARKER]` logger
  metrics.py         # thread-safe counters
  errors.py          # domain errors
  filters.py         # pluggable strategies
  formatters.py      # compact/verbose/json, field selection
  store.py           # UserStore with indexing, cache, snapshot
user_display_optimized.py   # API-compatible wrapper
user_display_original.py    # baseline (unchanged)
```

### Responsibilities
- **UserStore**: O(1) lookup via index, filtering with optional cache, thread-safe reads, snapshot/clone
- **formatters**: compact/verbose/json-like, include/exclude fields
- **filters**: strategy-based, case sensitivity control
- **config**: defaults + overrides
- **logging_utils**: `[MARKER]` logger
- **metrics**: counters for lookups, filters, cache hits/misses, validation errors
- **errors**: typed exceptions

## Features
- Multiple formatting profiles; field selection
- Extensible filtering strategies; case sensitivity control
- Validation and graceful skipping of malformed records
- Optional filter result caching (LRU)
- Snapshot/clone support in `UserStore`
- Thread-safe concurrent reads
- Metrics + structured logging

## Usage
```python
import user_display_optimized as ud

text = ud.display_users(users, show_all=True)            # compact by default
text_verbose = ud.display_users(users, verbose=True)     # verbose formatter
u = ud.get_user_by_id(users, 42)
filtered = ud.filter_users(users, {"role": "User", "status": "Active"})
export = ud.export_users_to_string(filtered)
```

For advanced usage:
```python
from user_display.store import UserStore
from user_display.filters import SimpleCriteriaFilter
from user_display.config import get_config

store = UserStore(users, config=get_config({"max_cache_size": 256}))
filtered = store.filter({"role": "User"}, strategy=SimpleCriteriaFilter())
text = ud.display_users(store.iter_users(), show_all=True)
```

## Tests
- Functional/API compatibility: `tests/test_api_compat.py`
- Formatters/filters: `tests/test_formatters.py`, `tests/test_filters.py`
- Store/caching/validation: `tests/test_store.py`
- Logging/metrics: `tests/test_logging_metrics.py`
- Concurrency/performance: `tests/test_concurrency_perf.py`

## Performance Targets
| Operation        | Target     | Notes (thresholds in tests) |
|------------------|------------|-----------------------------|
| Display 1,000    | < 100 ms   | test allows < 500 ms        |
| Filter 1,000     | < 10 ms    | test allows < 100 ms        |
| Lookup by ID     | < 1 ms     | test allows < 50 ms/1k ops  |

## Running Tests
```
# PowerShell
./run_tests.ps1
```
This will create `.venv`, install requirements, and run `pytest`.
