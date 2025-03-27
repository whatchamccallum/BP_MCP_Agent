# Test Result Caching

The Breaking Point MCP Agent includes a caching system for test results to improve performance when analyzing the same test results multiple times. This document explains how to configure and use the caching functionality.

## Overview

The caching system stores test results locally, avoiding repeated API calls to the Breaking Point system when the same test results are requested multiple times. This significantly improves performance for operations like:

- Generating multiple reports from the same test run
- Creating different visualizations of the same test data
- Comparing test results across multiple analyses
- Batch processing large numbers of tests

## Cache Configuration

The caching system can be configured with the following settings:

- **Cache Directory**: Location where cache files are stored
- **Cache TTL (Time-To-Live)**: How long cache entries remain valid (in seconds)
- **Cache Enable/Disable**: Whether to use caching at all

Default settings are defined in `src/constants.py`:

```python
DEFAULT_CACHE_DIR = os.path.join(os.path.expanduser("~"), ".bp_agent", "cache")
DEFAULT_CACHE_TTL = 3600  # 1 hour in seconds
CACHE_ENABLED = True
```

## Using Cache in Code

The cache is integrated with the API and analyzer components and is used automatically by default. When making API calls to retrieve test results, the system first checks if a valid cache entry exists before making a network request.

To use caching in your code:

```python
from src.api import BreakingPointAPI
from src.analyzer import get_test_result_summary

# Create API client
api = BreakingPointAPI(host, username, password)
api.login()

# Get test results with caching enabled (default)
results = api.get_test_results(test_id, run_id, use_cache=True)

# Get test results bypassing cache
fresh_results = api.get_test_results(test_id, run_id, use_cache=False)

# Get summary with caching enabled
summary = get_test_result_summary(api, test_id, run_id, use_cache=True)
```

## Command Line Cache Control

The command line interface includes options for controlling the cache:

```bash
# Run with caching (default)
python cli.py --host <host> --username <user> --password <pass> --test-id <id> --run-id <run> --generate-report

# Run without caching
python cli.py --host <host> --username <user> --password <pass> --test-id <id> --run-id <run> --generate-report --no-cache

# Clear cache before running
python cli.py --host <host> --username <user> --password <pass> --test-id <id> --run-id <run> --generate-report --clear-cache

# Show cache statistics
python cli.py --cache-stats
```

## Cache Management Tool

A dedicated cache management tool is provided to help maintain the cache:

```bash
# Show cache statistics
python cache_manager.py --stats

# Clear the entire cache
python cache_manager.py --clear

# Remove expired entries
python cache_manager.py --cleanup

# Remove entries older than a specific time (in seconds)
python cache_manager.py --max-age 86400  # Remove entries older than 1 day

# Invalidate a specific entry
python cache_manager.py --invalidate <test_id> <run_id>
```

## Cache Structure

Each test result is stored in a JSON file in the cache directory. The filename is derived from a hash of the test ID and run ID to ensure uniqueness.

Cache files store:
- Complete test results from the API
- Processed summaries for faster retrieval

## Performance Considerations

To get the best performance from the caching system:

1. For common operations on the same test data, enable caching to avoid repeated API calls
2. For critical analyses requiring fresh data, disable caching with `use_cache=False`
3. Run periodic cache cleanup to prevent the cache from growing too large
4. Consider reducing the cache TTL in environments with rapidly changing test results

## Troubleshooting

If you experience issues with the caching system:

1. Run `python cache_manager.py --stats` to check the cache status
2. Try clearing the cache with `python cache_manager.py --clear`
3. Check the log files for any cache-related errors
4. Ensure the cache directory is writeable by the current user