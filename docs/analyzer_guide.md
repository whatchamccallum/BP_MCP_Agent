# Analyzer Component Guide

This guide provides detailed information about the Breaking Point MCP Agent's analyzer component, which processes test results and generates reports and visualizations.

## Architecture Overview

The analyzer component is designed with a modular architecture that makes it easy to maintain and extend. It consists of several submodules:

1. **Core Module**: Provides the main `TestResultAnalyzer` class with core functionality
2. **Report Generators**: Generate different types of reports (standard, executive, detailed, compliance)
3. **Chart Generators**: Create visualizations of test results and comparisons

```
analyzer/
├── core.py                   # Core TestResultAnalyzer class
├── report_generators/        # Report generation modules
│   ├── standard.py           # Standard report generator
│   ├── executive.py          # Executive summary generator
│   ├── detailed.py           # Detailed report generator
│   └── compliance.py         # Compliance report generator
└── chart_generators/         # Chart generation modules
    └── generators.py         # Chart generation functions
```

The architecture follows a clean separation of concerns:

- **Interface Layer** (`analyzer.py`): Provides a simple API for users
- **Core Layer** (`core.py`): Implements the main analysis and orchestration logic
- **Generator Layer** (report and chart generators): Specialized modules for specific outputs

## Main Functions

The analyzer component provides the following functions through the `analyzer.py` interface:

### Creating an Analyzer Instance

```python
from src.analyzer import create_analyzer

# Create an analyzer instance
analyzer = create_analyzer(bp_api)
```

This creates a TestResultAnalyzer instance that can be used for multiple operations.

### Getting Test Results

```python
from src.analyzer import get_test_result_summary

# Get a summary of test results
summary = get_test_result_summary(bp_api, test_id, run_id)
```

The summary includes:
- Basic test information (name, type, start/end time, duration, status)
- Common metrics (throughput, latency)
- Test-specific metrics based on test type (strikes for security tests, transactions for application tests)

### Getting Raw Test Results

```python
from src.analyzer import get_raw_test_results

# Get complete raw test results from the API
raw_results = get_raw_test_results(bp_api, test_id, run_id)
```

This provides direct access to the raw test results from the Breaking Point API, which can be useful for custom analysis.

### Comparing Test Results

```python
from src.analyzer import compare_test_results

# Compare two test runs
comparison = compare_test_results(bp_api, 
                                 test_id1, run_id1,
                                 test_id2, run_id2)
```

This function provides a detailed comparison of metrics between two test runs, including:
- Differences in throughput and latency
- Percentage changes between test runs
- Test-specific metric comparisons (strikes, transactions)

### Generating Reports

```python
from src.analyzer import generate_report

# Generate a standard HTML report
report_path = generate_report(bp_api, test_id, run_id, 
                             output_format="html", 
                             report_type="standard",
                             output_dir="./reports")
```

The analyzer supports four report types:

1. **Standard**: A basic report with key metrics and test information
2. **Executive**: Executive summary with key findings and recommendations
3. **Detailed**: Comprehensive technical report with detailed metrics
4. **Compliance**: Security compliance-focused report with compliance status and remediation plans

Output formats include:
- HTML: Interactive web-based reports with styling
- CSV: Data-oriented reports for further processing
- PDF: Publication-quality reports (requires additional libraries)

### Generating Reports from Existing Summaries

```python
from src.analyzer import generate_report_from_summary

# Generate a report from an existing summary
report_path = generate_report_from_summary(bp_api, summary, 
                                         output_format="html", 
                                         report_type="executive",
                                         output_dir="./reports")
```

This allows you to generate reports from previously obtained test result summaries, which can be useful for batch processing or when working with cached results.

### Generating Charts

```python
from src.analyzer import generate_charts

# Generate charts for a test run
chart_files = generate_charts(bp_api, test_id, run_id, output_dir="./charts")
```

The chart generator creates visualizations for various metrics, including:
- Throughput over time
- Latency over time
- Security test results (blocked vs. allowed strikes)
- Transaction success rates

### Comparing Test Runs with Charts

```python
from src.analyzer import compare_charts

# Generate a throughput comparison chart
chart_path = compare_charts(bp_api,
                           test_id1, run_id1,
                           test_id2, run_id2,
                           chart_type="throughput",
                           output_dir="./charts")
```

Chart comparison types include:
- `throughput`: Compare throughput over time
- `latency`: Compare latency over time
- `strikes`: Compare security test results
- `transactions`: Compare transaction success rates

### Batch Processing Multiple Tests

```python
from src.analyzer import batch_process_tests

# Process multiple test runs and generate reports and charts
test_runs = [
    ("test_id_1", "run_id_1"),
    ("test_id_2", "run_id_2"),
    ("test_id_3", "run_id_3")
]

summaries = batch_process_tests(bp_api, test_runs, 
                              output_dir="./results", 
                              report_type="standard")
```

This function allows you to process multiple test runs in a single operation, generating reports and charts for each test run.

## Report Types in Detail

### Standard Report

The standard report provides a basic overview of test results, including:

- Test information (name, start/end time, duration, status)
- Performance metrics (throughput, latency)
- Test-specific metrics (strikes, transactions)

Example usage:
```python
report_path = generate_report(bp_api, test_id, run_id, 
                             output_format="html", 
                             report_type="standard")
```

### Executive Report

The executive report is designed for management and provides:

- Executive summary with overall test status
- Key findings based on test type
- Risk assessment (for security tests)
- Performance assessment (for application tests)
- Recommendations based on test results

Example usage:
```python
report_path = generate_report(bp_api, test_id, run_id, 
                             output_format="html", 
                             report_type="executive")
```

### Detailed Report

The detailed report provides comprehensive technical information, including:

- Test configuration details
- Detailed performance metrics
- Time series data analysis
- Test-specific detailed findings (security findings, performance analysis)
- Transaction breakdowns by type/endpoint

Example usage:
```python
report_path = generate_report(bp_api, test_id, run_id, 
                             output_format="html", 
                             report_type="detailed")
```

### Compliance Report

The compliance report focuses on security compliance and includes:

- Compliance assessment overview
- Compliance status (compliant/non-compliant)
- Mapping to compliance standards (PCI-DSS, NIST, ISO 27001)
- Detailed compliance metrics
- Remediation plan for non-compliant findings

Example usage:
```python
report_path = generate_report(bp_api, test_id, run_id, 
                             output_format="html", 
                             report_type="compliance")
```

## Implementation Details

### Core Architecture

The analyzer component uses a layered architecture:

1. **Interface Layer** (`analyzer.py`): Provides simple functions for users
2. **Core Layer** (`core.py`): Implements the main `TestResultAnalyzer` class
3. **Generator Layer** (report and chart generators): Specialized modules for specific outputs

### Data Flow

The data flow in the analyzer component:

1. Test results are retrieved from the Breaking Point API
2. Results are processed to extract relevant metrics
3. Metrics are analyzed and compared (if comparing multiple tests)
4. Reports and visualizations are generated based on the processed data

### Extending the Analyzer

To add new report types or chart types:

1. Create a new generator function in the appropriate module
2. Update the corresponding `__init__.py` file to export the new function
3. Update the core functionality to use the new generator

Example - Adding a new report type:

```python
# In report_generators/new_report.py
def generate_new_report(file, summary, raw_results):
    """Generate a new type of report"""
    # Implementation here
    
# In report_generators/__init__.py
from .new_report import generate_new_report

# In core.py, update the generate_report_from_summary method to handle the new type
if report_type == "new":
    generate_new_report(f, summary, raw_results)
```

## Advanced Usage

### Custom Report Styling

The HTML reports can be customized by modifying the CSS styles in the `generate_report_from_summary` method in `core.py`. Find the section with the HTML header and modify the styles as needed:

```python
f.write(f"""
<html>
<head>
    <title>Test Report: {summary['testName']} - {report_type.capitalize()}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        /* Modify or add styles here */
    </style>
</head>
<body>
```

### Integration with External Systems

The analyzer component can be integrated with external monitoring systems:

```python
from src.analyzer import create_analyzer, get_test_result_summary

# Get a test result summary
analyzer = create_analyzer(bp_api)
summary = get_test_result_summary(bp_api, test_id, run_id)

# Export to a monitoring system
success = analyzer.export_to_monitoring_system(
    summary, 
    system_url="https://monitoring.example.com/api/test-results",
    api_key="your-api-key"
)

if success:
    print("Test results exported successfully")
else:
    print("Failed to export test results")
```

This allows test results to be automatically sent to external monitoring systems for dashboards, alerts, and long-term trend analysis.

### Creating Custom Analysis Pipelines

You can create custom analysis pipelines by combining the various analyzer functions:

```python
from src.analyzer import get_test_result_summary, compare_test_results, generate_report

def analyze_weekly_tests(bp_api, tests, baseline_test, output_dir):
    """Analyze weekly tests against a baseline
    
    Args:
        bp_api: Breaking Point API instance
        tests: List of (test_id, run_id) tuples for weekly tests
        baseline_test: (test_id, run_id) tuple for baseline test
        output_dir: Output directory
    """
    # Get baseline results
    baseline_id, baseline_run = baseline_test
    baseline_results = get_test_result_summary(bp_api, baseline_id, baseline_run)
    
    # Analyze each test
    reports = []
    for test_id, run_id in tests:
        # Get test results
        results = get_test_result_summary(bp_api, test_id, run_id)
        
        # Compare with baseline
        comparison = compare_test_results(
            bp_api, baseline_id, baseline_run, test_id, run_id
        )
        
        # Generate reports
        report_path = generate_report(
            bp_api, test_id, run_id,
            output_format="html",
            report_type="detailed",
            output_dir=output_dir
        )
        
        reports.append({
            "test_id": test_id,
            "run_id": run_id,
            "report_path": report_path,
            "comparison": comparison
        })
    
    return reports
```

## Troubleshooting

### Common Issues

#### Report Generation Failures

If report generation fails:

1. Verify that you have the correct test ID and run ID
2. Check if the test has completed successfully
3. Ensure you have write permissions for the output directory

#### Chart Generation Issues

If chart generation fails:

1. Verify that matplotlib is installed correctly
2. Check if the required data (e.g., time series data) is available in the test results
3. Ensure you have write permissions for the output directory

#### Missing Data in Reports

If reports are missing expected data:

1. Check if the test type matches the expected metrics (e.g., strikes for security tests)
2. Verify that the test ran long enough to generate meaningful data
3. Use a more detailed report type (e.g., "detailed" instead of "standard")

### Debugging Tips

To debug issues with the analyzer component:

1. Enable debug logging:
   ```python
   import logging
   logging.basicConfig(level=logging.DEBUG)
   ```

2. Print raw test results:
   ```python
   raw_results = get_raw_test_results(bp_api, test_id, run_id)
   import json
   print(json.dumps(raw_results, indent=2))
   ```

3. Check the availability of time series data:
   ```python
   raw_results = get_raw_test_results(bp_api, test_id, run_id)
   if "timeseries" in raw_results:
       print("Time series data available")
       print(list(raw_results["timeseries"].keys()))
   else:
       print("No time series data available")
   ```

4. Verify outputs in interactive mode:
   ```python
   from src.analyzer import get_test_result_summary
   summary = get_test_result_summary(bp_api, test_id, run_id)
   
   # Check what metrics are available
   print("Available metrics:", list(summary.get("metrics", {}).keys()))
   
   # Inspect a specific metric
   if "throughput" in summary.get("metrics", {}):
       print("Throughput:", summary["metrics"]["throughput"])
   ```