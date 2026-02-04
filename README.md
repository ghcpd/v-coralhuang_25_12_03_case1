# user_display - Optimized user display package

This repository refactors a naive `input.py` into a modular, high-performance package.

## What's included

- `user_display_original.py`: baseline implementation (unaltered)
- `user_display/`: optimized package (store, formatters, filters, metrics, logging)
- `tests/`: pytest suite covering functionality, robustness, concurrency, and performance
- `run_tests.ps1`: one-click test run script (Windows PowerShell)
- `requirements.txt`: minimal test requirements

## Architecture

- `UserStore` (store.py): thread-safe store with O(1) ID lookup, filter strategies, optional caching and snapshot support.
- `formatters.py`: compact, verbose, and JSON-like formatters with field selection support.
- `filters.py`: pluggable filter strategy implementations and composite filter for multi-criteria searches.
- `logging_utils.py`: unified logger emitting `[MARKER]` in messages.
- `metrics.py`: simple counters for operations and cache behavior.

## Usage

Basic backward-compatible functions are exported via `user_display` package root:

from user_display import display_users, get_user_by_id, filter_users, export_users_to_string

Example:

text = display_users(users)
print(get_user_by_id(users, 3))

## Running tests

On Windows PowerShell:

./run_tests.ps1


## Performance targets

Targets are included in tests and should be validated on CI/hardware used.

