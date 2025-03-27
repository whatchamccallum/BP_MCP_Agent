# Breaking Point MCP Agent Plugins

This directory contains the plugin infrastructure for the Breaking Point MCP Agent. Plugins allow extending the functionality of the analyzer component to support different report types, chart formats, and analysis methods.

## Plugin Types

The following plugin types are supported:

- **Report Generators**: Create reports in various formats from test results
- **Chart Generators**: Create visualizations of test metrics
- **Analyzers**: Perform custom analysis on test results

## Built-in Plugins

The agent comes with the following built-in plugins:

### Report Generators
- `standard`: Basic test report
- `executive`: Executive summary report
- `detailed`: Detailed technical report
- `compliance`: Compliance-focused report

### Chart Generators
- `throughput`: Throughput performance charts
- `latency`: Latency performance charts
- `strikes`: Security strike charts
- `transactions`: Transaction success charts
- `comparison`: Comparison charts for multiple test runs

## Creating Custom Plugins

To create a custom plugin:

1. Create a new Python module
2. Import the base classes from `src.analyzer.plugins.base`
3. Implement the appropriate interface for your plugin type
4. Include a `register_plugins` function that registers your plugins

### Example: Custom Report Generator

```python
"""
Example of a custom report generator plugin
"""

from typing import Dict, Any
from src.analyzer.plugins.base import ReportGenerator, TestSummary, PluginManager

class CustomReportGenerator(ReportGenerator):
    """Custom report generator that creates a specialized report"""
    
    def generate(self, summary: TestSummary, raw_results: Dict[str, Any], 
                output_format: str, output_file: str) -> str:
        """Generate a custom report
        
        Args:
            summary: Test summary data
            raw_results: Raw test results
            output_format: Output format (text, html, csv, etc.)
            output_file: Path to output file
            
        Returns:
            str: Path to generated report
        """
        # Implementation here
        return output_file

def register_plugins(manager: PluginManager) -> None:
    """Register plugins with the plugin manager
    
    Args:
        manager: Plugin manager instance
    """
    # Register your custom plugins
    manager.register_report_generator("custom", CustomReportGenerator())
```

## Loading Custom Plugins

Custom plugins can be loaded by calling the `discover_plugins` function with a list of directories containing your plugin modules:

```python
from src.analyzer.plugins.registry import discover_plugins

# Load plugins from a custom directory
discover_plugins(["/path/to/plugins"])
```

## Plugin Manager API

The plugin manager provides the following methods:

- `register_report_generator(name, generator)`: Register a report generator
- `register_chart_generator(name, generator)`: Register a chart generator
- `register_analyzer(name, analyzer)`: Register an analyzer
- `get_report_generator(name)`: Get a report generator by name
- `get_chart_generator(name)`: Get a chart generator by name
- `get_analyzer(name)`: Get an analyzer by name

You can access the plugin manager instance using:

```python
from src.analyzer.plugins.registry import get_plugin_manager

manager = get_plugin_manager()
```
