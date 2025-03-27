# Breaking Point MCP Agent Usage Guide

This guide provides detailed instructions and examples for using the Breaking Point MCP Agent with Claude Desktop AI.

## Table of Contents

1. [Basic Usage Flow](#basic-usage-flow)
2. [Authentication](#authentication)
3. [Creating and Running Tests](#creating-and-running-tests)
4. [Network Topology Configuration](#network-topology-configuration)
5. [SuperFlow Management](#superflow-management)
6. [Analyzing Test Results](#analyzing-test-results)
7. [Common Workflows](#common-workflows)
8. [Troubleshooting](#troubleshooting)

## Basic Usage Flow

The typical workflow when using the Breaking Point MCP Agent:

1. Connect to the Breaking Point system
2. Create or select network topologies
3. Create or select test components (SuperFlows, strike lists, etc.)
4. Configure and run tests
5. Analyze test results
6. Generate reports and visualizations

## Authentication

To connect to a Breaking Point system:

```python
from bp_mcp_agent.api import BreakingPointAPI

# Initialize API connection
bp_api = BreakingPointAPI(host="192.168.1.100", username="admin", password="password")

# Login
if bp_api.login():
    print("Successfully connected to Breaking Point")
else:
    print("Failed to connect")

# When finished
bp_api.logout()
```

It's recommended to use a context manager or try/finally block to ensure proper logout:

```python
try:
    bp_api.login()
    # Perform operations
finally:
    bp_api.logout()
```

## Creating and Running Tests

### Strike Test (Security Testing)

Strike tests use security strike lists to test network security devices.

```python
from bp_mcp_agent.api import BreakingPointAPI
from bp_mcp_agent.test_builder import TestBuilder
from bp_mcp_agent.topology import NetworkTopology

# Initialize API
bp_api = BreakingPointAPI(host="192.168.1.100", username="admin", password="password")
bp_api.login()

# Create a test builder
builder = TestBuilder(bp_api)

# Configure topology
topology = NetworkTopology()
topology.add_client_network("Client-Net", "10.0.1.0/24", 100)
topology.add_server_network("Server-Net", "10.0.2.0/24", 10)

# Create the strike test
test = builder.create_strike_test(
    name="Strike Test 1",
    strike_list_id="SL_123",  # ID of a strike list in your Breaking Point system
    topology=topology,
    duration=300  # 5 minutes
)

# Run the test
result = bp_api.run_test(test["id"])
print(f"Test started with run ID: {result['runId']}")

# Logout when done
bp_api.logout()
```

### Application Simulation Test

Application Simulation tests model real-world application traffic.

```python
from bp_mcp_agent.api import BreakingPointAPI
from bp_mcp_agent.test_builder import TestBuilder
from bp_mcp_agent.topology import NetworkTopology

# Initialize API
bp_api = BreakingPointAPI(host="192.168.1.100", username="admin", password="password")
bp_api.login()

# Create a test builder
builder = TestBuilder(bp_api)

# Configure topology
topology = NetworkTopology()
topology.add_client_network("Client-Net", "10.0.1.0/24", 250)
topology.add_server_network("Server-Net", "10.0.2.0/24", 50)

# Create the application simulation test
test = builder.create_app_sim_test(
    name="Web Traffic Test",
    app_profile_id="AP_456",  # ID of an application profile in your Breaking Point system
    topology=topology,
    duration=600  # 10 minutes
)

# Run the test
result = bp_api.run_test(test["id"])
print(f"Test started with run ID: {result['runId']}")

# Logout when done
bp_api.logout()
```

### Bandwidth Test

Bandwidth tests help assess network performance under high throughput conditions.

```python
from bp_mcp_agent.api import BreakingPointAPI
from bp_mcp_agent.test_builder import TestBuilder
from bp_mcp_agent.topology import NetworkTopology

# Initialize API
bp_api = BreakingPointAPI(host="192.168.1.100", username="admin", password="password")
bp_api.login()

# Create a test builder
builder = TestBuilder(bp_api)

# Configure topology
topology = NetworkTopology()
topology.add_client_network("Client-Net", "10.0.1.0/24", 10)
topology.add_server_network("Server-Net", "10.0.2.0/24", 10)

# Create the bandwidth test
test = builder.create_bandwidth_test(
    name="Gigabit Throughput Test",
    bandwidth_component_id="BW_789",  # ID of a bandwidth component
    topology=topology,
    duration=300,  # 5 minutes
    rate=1000,  # 1 Gbps
    frame_size=1500
)

# Run the test
result = bp_api.run_test(test["id"])
print(f"Test started with run ID: {result['runId']}")

# Logout when done
bp_api.logout()
```

## Network Topology Configuration

The `NetworkTopology` class helps you create and manage network configurations:

```python
from bp_mcp_agent.topology import NetworkTopology

# Create a new topology
topology = NetworkTopology()

# Add a client network
topology.add_client_network(
    name="Internal-Clients",
    cidr="192.168.10.0/24",
    client_count=500
)

# Add a server network
topology.add_server_network(
    name="Data-Center",
    cidr="10.50.0.0/16",
    server_count=50
)

# Add a DMZ network
topology.add_dmz_network(
    name="DMZ-1",
    cidr="172.16.1.0/24"
)

# Validate the topology
if topology.validate():
    print("Topology is valid")
else:
    print("Topology is invalid")

# Save to file for later use
topology.to_file("my_topology.yaml")

# Load from file
new_topology = NetworkTopology()
new_topology.from_file("my_topology.yaml")
```

## SuperFlow Management

SuperFlows define the application traffic patterns:

```python
from bp_mcp_agent.api import BreakingPointAPI
from bp_mcp_agent.superflow import SuperFlowManager

# Initialize API
bp_api = BreakingPointAPI(host="192.168.1.100", username="admin", password="password")
bp_api.login()

# Create a SuperFlow manager
sf_manager = SuperFlowManager(bp_api)

# Create a basic HTTP SuperFlow
http_flow = sf_manager.create_basic_superflow(
    name="Basic Web Browsing",
    protocol="HTTP"
)

# Create a more complex HTTP SuperFlow with multiple transactions
web_transactions = [
    {
        "method": "GET",
        "path": "/",
        "status_code": 200,
        "content_type": "text/html"
    },
    {
        "method": "GET",
        "path": "/images/logo.png",
        "status_code": 200,
        "content_type": "image/png"
    },
    {
        "method": "POST",
        "path": "/login",
        "request_body": "username=user&password=pass",
        "status_code": 302,
        "response_headers": {"Location": "/dashboard"}
    }
]

advanced_flow = sf_manager.create_http_superflow(
    name="Web Portal Login",
    transactions=web_transactions
)

# Logout when done
bp_api.logout()
```

## Analyzing Test Results

The Analyzer component helps process and visualize test results:

```python
from bp_mcp_agent.api import BreakingPointAPI
from bp_mcp_agent.analyzer import get_test_result_summary, generate_report, generate_charts

# Initialize API
bp_api = BreakingPointAPI(host="192.168.1.100", username="admin", password="password")
bp_api.login()

# Get test result summary
test_id = "test_123"
run_id = "run_456"
summary = get_test_result_summary(bp_api, test_id, run_id)

# Print basic metrics
print(f"Test: {summary['testName']}")
print(f"Status: {summary['status']}")
print(f"Duration: {summary['duration']} seconds")

if "throughput" in summary["metrics"]:
    throughput = summary["metrics"]["throughput"]["average"]
    print(f"Average Throughput: {throughput} Mbps")

if "latency" in summary["metrics"]:
    latency = summary["metrics"]["latency"]["average"]
    print(f"Average Latency: {latency} ms")

# Generate a report
report_path = generate_report(
    bp_api, 
    test_id, 
    run_id, 
    output_format="html", 
    report_type="executive",
    output_dir="./reports"
)
print(f"Report generated: {report_path}")

# Generate charts
chart_paths = generate_charts(
    bp_api,
    test_id,
    run_id,
    output_dir="./charts"
)
print(f"Generated {len(chart_paths)} charts")

# Logout when done
bp_api.logout()
```

### Comparing Test Results

To compare results from different tests:

```python
from bp_mcp_agent.api import BreakingPointAPI
from bp_mcp_agent.analyzer import compare_test_results, compare_charts

# Initialize API
bp_api = BreakingPointAPI(host="192.168.1.100", username="admin", password="password")
bp_api.login()

# Compare two test runs
test_id1 = "test_123"
run_id1 = "run_456"
test_id2 = "test_123"  # Same test, different run
run_id2 = "run_789"

comparison = compare_test_results(
    bp_api,
    test_id1, run_id1,
    test_id2, run_id2
)

# Print comparison results
print(f"Comparing {comparison['test1']['testName']} vs {comparison['test2']['testName']}")

if "throughput" in comparison["metrics"]:
    diff = comparison["metrics"]["throughput"]["difference"]["average"]
    pct = comparison["metrics"]["throughput"]["difference"]["percentage"]
    print(f"Throughput difference: {diff} Mbps ({pct:.2f}%)")

# Generate a comparison chart
chart_path = compare_charts(
    bp_api,
    test_id1, run_id1,
    test_id2, run_id2,
    chart_type="throughput",
    output_dir="./comparison_charts"
)
print(f"Comparison chart generated: {chart_path}")

# Logout when done
bp_api.logout()
```

## Common Workflows

### Running a Security Audit

```python
from bp_mcp_agent.api import BreakingPointAPI
from bp_mcp_agent.test_builder import TestBuilder
from bp_mcp_agent.topology import NetworkTopology
from bp_mcp_agent.analyzer import generate_report
import time

# Initialize API
bp_api = BreakingPointAPI(host="192.168.1.100", username="admin", password="password")
bp_api.login()

try:
    # Create test builder
    builder = TestBuilder(bp_api)
    
    # Configure topology
    topology = NetworkTopology()
    topology.add_client_network("Internal", "10.0.1.0/24", 100)
    topology.add_server_network("External", "203.0.113.0/24", 10)
    
    # Create a strike test
    test = builder.create_strike_test(
        name="Security Audit",
        strike_list_id="SL_ALL_STRIKES",  # Using all strikes
        topology=topology,
        duration=1800  # 30 minutes
    )
    
    # Run the test
    result = bp_api.run_test(test["id"])
    test_id = test["id"]
    run_id = result["runId"]
    
    print(f"Security audit started with run ID: {run_id}")
    
    # Wait for test to complete
    status = "running"
    while status == "running":
        time.sleep(30)  # Check every 30 seconds
        test_results = bp_api.get_test_results(test_id, run_id)
        status = test_results.get("status")
        print(f"Test status: {status}")
    
    # Generate compliance report
    if status == "completed":
        report_path = generate_report(
            bp_api,
            test_id,
            run_id,
            output_format="html",
            report_type="compliance",
            output_dir="./security_reports"
        )
        print(f"Compliance report generated: {report_path}")
    else:
        print(f"Test ended with status: {status}")
        
finally:
    # Ensure logout happens
    bp_api.logout()
```

### Performance Baseline Testing

```python
from bp_mcp_agent.api import BreakingPointAPI
from bp_mcp_agent.test_builder import TestBuilder
from bp_mcp_agent.topology import NetworkTopology
from bp_mcp_agent.analyzer import batch_process_tests
import time

# Initialize API
bp_api = BreakingPointAPI(host="192.168.1.100", username="admin", password="password")
bp_api.login()

try:
    # Create test builder
    builder = TestBuilder(bp_api)
    
    # Configure topology
    topology = NetworkTopology()
    topology.add_client_network("Users", "10.0.1.0/24", 1000)
    topology.add_server_network("Servers", "10.0.2.0/24", 100)
    
    # Create tests with different loads
    test_runs = []
    
    # Create and run tests at different loads
    for load in [100, 500, 1000, 5000]:
        test_name = f"Baseline-{load}Mbps"
        
        test = builder.create_bandwidth_test(
            name=test_name,
            bandwidth_component_id="BW_TCP",
            topology=topology,
            duration=300,  # 5 minutes
            rate=load  # Mbps
        )
        
        print(f"Running test: {test_name}")
        result = bp_api.run_test(test["id"])
        test_runs.append((test["id"], result["runId"]))
        
        # Wait for test to complete
        status = "running"
        while status == "running":
            time.sleep(30)
            test_results = bp_api.get_test_results(test["id"], result["runId"])
            status = test_results.get("status")
            print(f"Test {test_name} status: {status}")
    
    # Process all test results
    print("Processing all test results...")
    results = batch_process_tests(
        bp_api,
        test_runs,
        output_dir="./baseline_reports",
        report_type="detailed"
    )
    
    print(f"Processed {len(results)} test runs")
    
finally:
    # Ensure logout happens
    bp_api.logout()
```

## Troubleshooting

### Common Issues and Solutions

1. **API Connection Errors**
   - Verify the hostname is correct
   - Check network connectivity
   - Ensure credentials are valid
   - Verify the Breaking Point system is running

2. **Test Creation Failures**
   - Check all required parameters
   - Validate network topology
   - Ensure referenced resources (strike lists, app profiles) exist

3. **Test Execution Issues**
   - Check system resources on Breaking Point
   - Verify test configuration
   - Check licenses for specific features

4. **Result Analysis Problems**
   - Ensure the test has completed
   - Check for proper test ID and run ID
   - Verify output directory permissions for reports and charts

### Enabling Debug Logging

To get more detailed logs:

```python
import logging

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='bp_agent.log'
)
```

### Getting Help

For more assistance:
- Check the Breaking Point API documentation
- Review the [API Reference](api_reference.md)
- Examine the [Architecture Diagrams](architecture_diagrams.md)
