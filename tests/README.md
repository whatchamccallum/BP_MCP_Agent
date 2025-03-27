# Testing the Breaking Point MCP Agent

This directory contains tests for the Breaking Point MCP Agent.

## Unit Tests

The unit tests verify that individual components work correctly in isolation.

### Running All Tests

To run all tests:

```bash
cd <project-root>
python -m unittest discover tests
```

### Running Specific Tests

To run a specific test file:

```bash
python -m unittest tests.test_analyzer
```

To run a specific test case or method:

```bash
python -m unittest tests.test_analyzer.TestAnalyzer.test_get_test_result_summary
```

## Validation Script

The validation script (`validate_analyzer.py`) can be used to test the analyzer with a real Breaking Point system. This is useful for integration testing.

### Running the Validation Script

```bash
python validate_analyzer.py <host> <username> <password> <test_id> <run_id> [test_id2] [run_id2]
```

Example:

```bash
python validate_analyzer.py 192.168.1.100 admin password 123 456
```

To test comparison functionality, provide a second test and run ID:

```bash
python validate_analyzer.py 192.168.1.100 admin password 123 456 789 012
```

## Adding New Tests

When adding new functionality to the Breaking Point MCP Agent, consider adding tests for:

1. **Unit tests**: Test individual functions in isolation
2. **Integration tests**: Test interaction between components
3. **System tests**: Test the entire system with real or mocked Breaking Point APIs

### Test Organization Guidelines

- Each test file should focus on a single component
- Test file names should follow the pattern `test_<component>.py`
- Test classes should inherit from `unittest.TestCase`
- Test methods should start with `test_`
- Use descriptive method names to clarify what is being tested

### Mocking Guidelines

When testing components that depend on external systems like the Breaking Point API:

1. Use `unittest.mock.MagicMock` to create mock objects
2. Configure the mocks with realistic return values
3. Use `patch` to temporarily replace functions or classes
4. Verify that the mocks were called correctly as part of your assertions

Example:

```python
from unittest.mock import MagicMock, patch
from src.api import BreakingPointAPI

# Create a mock API instance
bp_api = MagicMock(spec=BreakingPointAPI)
bp_api.get_test_results.return_value = {"testName": "Test 1", "status": "completed"}

# Use patch to temporarily replace a function
with patch("src.analyzer.generate_charts") as mock_generate_charts:
    mock_generate_charts.return_value = ["chart1.png", "chart2.png"]
    
    # Test your code that uses generate_charts
    
    # Verify the mock was called correctly
    mock_generate_charts.assert_called_once_with(bp_api, "test1", "run1", "./output")
```
