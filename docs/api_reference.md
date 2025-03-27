# API Reference

This document provides detailed reference information for the Breaking Point MCP Agent API.

## Table of Contents

- [BreakingPointAPI](#breakingpointapi)
- [TestBuilder](#testbuilder)
- [NetworkTopology](#networktopology)
- [SuperFlow](#superflow)
- [TestResultAnalyzer](#testresultanalyzer)
- [Analyzer Functions](#analyzer-functions)

## BreakingPointAPI

The `BreakingPointAPI` class provides an interface to the Breaking Point system's REST API.

### Constructor

```python
BreakingPointAPI(host, username, password, port=443, verify_ssl=True)
```

Parameters:
- `host` (str): Hostname or IP address of the Breaking Point system
- `username` (str): Username for authentication
- `password` (str): Password for authentication
- `port` (int, optional): API port (default: 443)
- `verify_ssl` (bool, optional): Whether to verify SSL certificates (default: True)

### Methods

#### connect()

Establishes a connection to the Breaking Point system.

```python
connect() -> bool
```

Returns:
- `bool`: True if connection successful, False otherwise

#### get_test_results(test_id, run_id)

Retrieves results for a specific test run.

```python
get_test_results(test_id, run_id) -> dict
```

Parameters:
- `test_id` (str): Test ID
- `run_id` (str): Run ID

Returns:
- `dict`: Test results data

## TestBuilder

The `TestBuilder` class is used to create and manage test configurations.

### Constructor

```python
TestBuilder(bp_api)
```

Parameters:
- `bp_api` (BreakingPointAPI): Breaking Point API instance

### Methods

#### create_strike_test(name, strike_list, duration=60, concurrent=10)

Creates a security strike test.

```python
create_strike_test(name, strike_list, duration=60, concurrent=10) -> str
```

Parameters:
- `name` (str): Test name
- `strike_list` (list): List of strikes or categories
- `duration` (int, optional): Test duration in seconds (default: 60)
- `concurrent` (int, optional): Concurrent strikes (default: 10)

Returns:
- `str`: Test ID

#### create_appsim_test(name, app_profiles, duration=60, concurrent_users=100)

Creates an application simulation test.

```python
create_appsim_test(name, app_profiles, duration=60, concurrent_users=100) -> str
```

Parameters:
- `name` (str): Test name
- `app_profiles` (list): List of application profiles
- `duration` (int, optional): Test duration in seconds (default: 60)
- `concurrent_users` (int, optional): Concurrent users (default: 100)

Returns:
- `str`: Test ID

#### run_test(test_id)

Runs a test by ID.

```python
run_test(test_id) -> str
```

Parameters:
- `test_id` (str): Test ID

Returns:
- `str`: Run ID

#### get_test_status(test_id, run_id)

Gets the status of a test run.

```python
get_test_status(test_id, run_id) -> str
```

Parameters:
- `test_id` (str): Test ID
- `run_id` (str): Run ID

Returns:
- `str`: Test status (e.g., "running", "completed", "failed")

## NetworkTopology

The `NetworkTopology` class manages network configurations for tests.

### Constructor

```python
NetworkTopology(bp_api)
```

Parameters:
- `bp_api` (BreakingPointAPI): Breaking Point API instance

### Methods

#### create_topology(name, interfaces)

Creates a network topology configuration.

```python
create_topology(name, interfaces) -> str
```

Parameters:
- `name` (str): Topology name
- `interfaces` (dict): Interface definitions

Returns:
- `str`: Topology ID

## SuperFlow

The `SuperFlow` class manages traffic flow configurations.

### Constructor

```python
SuperFlow(bp_api)
```

Parameters:
- `bp_api` (BreakingPointAPI): Breaking Point API instance

### Methods

#### create_superflow(name, protocol, actions)

Creates a SuperFlow configuration.

```python
create_superflow(name, protocol, actions) -> str
```

Parameters:
- `name` (str): SuperFlow name
- `protocol` (str): Base protocol
- `actions` (list): Flow actions

Returns:
- `str`: SuperFlow ID

## TestResultAnalyzer

The `TestResultAnalyzer` class processes and analyzes test results.

### Constructor

```python
TestResultAnalyzer(bp_api)
```

Parameters:
- `bp_api` (BreakingPointAPI): Breaking Point API instance

### Methods

#### get_test_result_summary(test_id, run_id)

Gets a summary of test results.

```python
get_test_result_summary(test_id, run_id) -> dict
```

Parameters:
- `test_id` (str): Test ID
- `run_id` (str): Run ID

Returns:
- `dict`: Test result summary with metrics

#### compare_test_results(result1, result2)

Compares two test results.

```python
compare_test_results(result1, result2) -> dict
```

Parameters:
- `result1` (dict): First test result summary
- `result2` (dict): Second test result summary

Returns:
- `dict`: Comparison results with differences and percentages

#### generate_report(test_id, run_id, output_format="html", report_type="standard")

Generates a report for a test run.

```python
generate_report(test_id, run_id, output_format="html", report_type="standard") -> str
```

Parameters:
- `test_id` (str): Test ID
- `run_id` (str): Run ID
- `output_format` (str, optional): Output format ("html", "pdf", "csv") (default: "html")
- `report_type` (str, optional): Report type ("standard", "executive", "detailed", "compliance") (default: "standard")

Returns:
- `str`: Path to the generated report file

#### generate_charts(test_id, run_id, output_dir="./")

Generates charts for test results.

```python
generate_charts(test_id, run_id, output_dir="./") -> list
```

Parameters:
- `test_id` (str): Test ID
- `run_id` (str): Run ID
- `output_dir` (str, optional): Output directory (default: "./")

Returns:
- `list`: Paths to generated chart files

#### compare_charts(test_id1, run_id1, test_id2, run_id2, chart_type, output_dir="./")

Generates a comparison chart for two test runs.

```python
compare_charts(test_id1, run_id1, test_id2, run_id2, chart_type, output_dir="./") -> str
```

Parameters:
- `test_id1` (str): First test ID
- `run_id1` (str): First run ID
- `test_id2` (str): Second test ID
- `run_id2` (str): Second run ID
- `chart_type` (str): Chart type ("throughput", "latency", "strikes", "transactions")
- `output_dir` (str, optional): Output directory (default: "./")

Returns:
- `str`: Path to the generated chart file

## Analyzer Functions

The `analyzer.py` module provides convenient functions that wrap the `TestResultAnalyzer` class.

### create_analyzer(bp_api)

Creates a test result analyzer instance.

```python
create_analyzer(bp_api) -> TestResultAnalyzer
```

Parameters:
- `bp_api` (BreakingPointAPI): Breaking Point API instance

Returns:
- `TestResultAnalyzer`: Analyzer instance

### get_test_result_summary(bp_api, test_id, run_id)

Gets a summary of test results.

```python
get_test_result_summary(bp_api, test_id, run_id) -> dict
```

Parameters:
- `bp_api` (BreakingPointAPI): Breaking Point API instance
- `test_id` (str): Test ID
- `run_id` (str): Run ID

Returns:
- `dict`: Test result summary

### compare_test_results(bp_api, test_id1, run_id1, test_id2, run_id2)

Compares two test results.

```python
compare_test_results(bp_api, test_id1, run_id1, test_id2, run_id2) -> dict
```

Parameters:
- `bp_api` (BreakingPointAPI): Breaking Point API instance
- `test_id1` (str): First test ID
- `run_id1` (str): First run ID
- `test_id2` (str): Second test ID
- `run_id2` (str): Second run ID

Returns:
- `dict`: Comparison results

### generate_report(bp_api, test_id, run_id, output_format="html", report_type="standard")

Generates a report for a test run.

```python
generate_report(bp_api, test_id, run_id, output_format="html", report_type="standard") -> str
```

Parameters:
- `bp_api` (BreakingPointAPI): Breaking Point API instance
- `test_id` (str): Test ID
- `run_id` (str): Run ID
- `output_format` (str, optional): Output format ("html", "pdf", "csv") (default: "html")
- `report_type` (str, optional): Report type ("standard", "executive", "detailed", "compliance") (default: "standard")

Returns:
- `str`: Path to the generated report file

### generate_charts(bp_api, test_id, run_id, output_dir="./")

Generates charts for test results.

```python
generate_charts(bp_api, test_id, run_id, output_dir="./") -> list
```

Parameters:
- `bp_api` (BreakingPointAPI): Breaking Point API instance
- `test_id` (str): Test ID
- `run_id` (str): Run ID
- `output_dir` (str, optional): Output directory (default: "./")

Returns:
- `list`: Paths to generated chart files

### compare_charts(bp_api, test_id1, run_id1, test_id2, run_id2, chart_type, output_dir="./")

Generates a comparison chart for two test runs.

```python
compare_charts(bp_api, test_id1, run_id1, test_id2, run_id2, chart_type, output_dir="./") -> str
```

Parameters:
- `bp_api` (BreakingPointAPI): Breaking Point API instance
- `test_id1` (str): First test ID
- `run_id1` (str): First run ID
- `test_id2` (str): Second test ID
- `run_id2` (str): Second run ID
- `chart_type` (str): Chart type ("throughput", "latency", "strikes", "transactions")
- `output_dir` (str, optional): Output directory (default: "./")

Returns:
- `str`: Path to the generated chart file
