# Breaking Point MCP Agent

A Management Control Protocol (MCP) agent for Ixia Breaking Point to create, control, monitor, and analyze traffic test scenarios with Claude Desktop AI.

## Overview

The Breaking Point MCP Agent enables seamless interaction with Ixia Breaking Point through Claude Desktop AI. It facilitates creating and managing various traffic test scenarios including:

- Strike Tests (security/vulnerability testing)
- Application Simulations
- Client Simulations
- Bandwidth Tests
- Advanced Security Tests

## Features

- **Test Creation and Management**: Create and run different types of traffic tests
- **Network Configuration**: Define and modify network topologies
- **SuperFlow Management**: Create and customize traffic flows
- **Results Analysis**: Analyze test results with comprehensive reports and visualizations
- **Visual Reporting**: Generate charts for metrics comparison
- **Result Caching**: Improve performance with local caching of test results
- **Asynchronous API**: Execute operations concurrently for improved performance
- **Plugin Architecture**: Extend functionality with custom plugins for reports and charts

## Project Structure

```
BP_MCP_Agent/
├── src/                          # Source code
│   ├── api.py                    # Breaking Point API integration
│   ├── api_async.py              # Asynchronous API integration
│   ├── analyzer.py               # Test result analyzer interface
│   ├── analyzer_async.py         # Asynchronous analyzer interface
│   ├── analyzer/                 # Analyzer modules
│   │   ├── core.py               # Core analyzer implementation
│   │   ├── plugins/              # Plugin system for extensibility
│   │   │   ├── base.py           # Plugin interfaces
│   │   │   ├── chart_generators.py  # Chart generation plugins
│   │   │   ├── report_generators.py # Report generation plugins
│   │   │   └── registry.py       # Plugin registration system
│   ├── superflow.py              # SuperFlow management
│   ├── test_builder.py           # Test creation and management
│   └── topology.py               # Network topology configuration
├── examples/                     # Example scripts
│   ├── async_operations.py       # Example of async API usage
│   ├── plugin_demo.py            # Example of plugin system usage
│   └── plugins/                  # Custom plugin examples
├── docs/                         # Documentation
│   ├── installation_guide.md     # Installation instructions
│   ├── usage_guide.md            # Usage examples and instructions
│   ├── analyzer_guide.md         # Guide for the analyzer component
│   ├── plugin_guide.md           # Guide for creating plugins
│   └── api_reference.md          # API reference documentation
├── tests/                        # Test scripts
└── requirements.txt              # Python dependencies
```

## Installation

See the [Installation Guide](docs/installation_guide.md) for detailed instructions.

## Usage

See the [Usage Guide](docs/usage_guide.md) for examples of how to use the agent with Claude Desktop AI.

## Analyzer Component

The BP MCP Agent includes a powerful analyzer component that processes test results and generates reports and visualizations. Key capabilities include:

- Generate summaries of test results
- Compare results from different test runs
- Generate various report types (standard, executive, detailed, compliance)
- Create visualizations of test metrics
- Generate comparison charts
- Cache test results for improved performance

See the [Analyzer Guide](docs/analyzer_guide.md) for detailed information on using the analyzer.

## Plugin System

The agent includes a flexible plugin system that allows extending functionality:

- **Report Generators**: Create custom report formats and templates
- **Chart Generators**: Create specialized visualizations for test data
- **Analyzer Plugins**: Implement custom analysis algorithms

See the [Plugin Guide](docs/plugin_guide.md) for information on creating and using plugins.

## Asynchronous API

The agent includes an asynchronous API that enables concurrent operations:

- Run multiple tests simultaneously
- Process multiple test results in parallel
- Significantly improved performance for batch operations

## Caching System

The agent includes a caching system that improves performance when working with the same test results multiple times. Features include:

- Automatic caching of API responses and analysis results
- Cache management through command line options
- Configurable cache TTL (time-to-live)
- Cache invalidation mechanisms

See the [Caching Guide](docs/caching.md) for detailed information on using and configuring the cache.

## Requirements

- Python 3.7+
- Breaking Point system with API access
- Claude Desktop AI with agent support
- Required Python packages:
  - requests >= 2.25.0
  - aiohttp >= 3.8.0 (for async operations)
  - matplotlib >= 3.4.0
  - pandas >= 1.2.0

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
