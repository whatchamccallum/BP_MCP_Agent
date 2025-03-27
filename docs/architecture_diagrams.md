# Architecture Diagrams

This document provides architectural diagrams to help visualize the structure and interaction of components in the Breaking Point MCP Agent.

## Project Structure

The Breaking Point MCP Agent is structured as follows:

```
BP_MCP_Agent/
├── src/                          # Source code
│   ├── api.py                    # Breaking Point API integration
│   ├── analyzer.py               # Test result analyzer interface
│   ├── analyzer/                 # Analyzer modules
│   │   ├── core.py               # Core analyzer implementation
│   │   ├── report_generators/    # Report generation modules
│   │   └── chart_generators/     # Chart generation modules
│   ├── superflow.py              # SuperFlow management
│   ├── test_builder.py           # Test creation and management
│   └── topology.py               # Network topology configuration
├── docs/                         # Documentation
├── tests/                        # Test scripts
└── requirements.txt              # Python dependencies
```

## Component Diagram

Below is a component diagram showing the major components of the system and their relationships:

```
+-----------------+     +---------------------+
|                 |     |                     |
| Claude Desktop  |     |  Breaking Point     |
|      AI         |     |      System         |
|                 |     |                     |
+-------+---------+     +---------+-----------+
        |                         |
        |                         |
        v                         v
+-------+-------------------------+-----------+
|                                             |
|            BP_MCP_Agent                     |
|                                             |
| +---------------+      +------------------+ |
| |               |      |                  | |
| | Test Builder  |<---->|  API Interface   | |
| |               |      |                  | |
| +------+--------+      +------------------+ |
|        |                         ^          |
|        v                         |          |
| +------+--------+     +----------+-------+  |
| |               |     |                  |  |
| |  Network      |     |    SuperFlow     |  |
| |  Topology     |     |    Manager       |  |
| |               |     |                  |  |
| +---------------+     +------------------+  |
|                                             |
|                   +------------+            |
|                   |            |            |
|                   |  Analyzer  |            |
|                   |            |            |
|                   +---+--------+            |
|                       |                     |
|          +------------+-----------+         |
|          |                        |         |
| +--------v-------+    +-----------v-----+   |
| |                |    |                 |   |
| | Report         |    | Chart           |   |
| | Generators     |    | Generators      |   |
| |                |    |                 |   |
| +----------------+    +-----------------+   |
|                                             |
+---------------------------------------------+
```

## Analyzer Component Architecture

The analyzer component has the following architecture:

```
+---------------------------------------------------+
|                                                   |
|                 analyzer.py                       |
|        (High-level interface functions)           |
|                                                   |
+-----------------------+-------------------------+-+
                        |
                        v
+---------------------------------------------------+
|                                                   |
|                    core.py                        |
|         (TestResultAnalyzer class)                |
|                                                   |
+----------------+---------------------+------------+
                 |                     |
                 v                     v
+----------------+------+  +-----------+-----------+
|                       |  |                       |
| report_generators/    |  | chart_generators/     |
|                       |  |                       |
+------+--------+-------+  +-------+----------+----+
       |        |                  |          |
       v        v                  v          v
+------+--+ +---+-------+  +-------+--+ +-----+------+
|         | |           |  |          | |            |
| standard| | executive |  | generate | | compare    |
|         | |           |  | charts   | | charts     |
+---------+ +-----------+  +----------+ +------------+
       |        |
       v        v
+------+--+ +---+--------+
|         | |            |
| detailed| | compliance |
|         | |            |
+---------+ +------------+
```

## Sequence Diagram: Test Execution and Analysis

This sequence diagram illustrates the typical flow for executing a test and analyzing the results:

```
+--------+    +------------+    +---------------+    +------------+    +---------+
| Client |    | TestBuilder|    | BreakingPoint |    | Analyzer   |    | Report  |
|        |    |            |    | API           |    |            |    | Generator|
+---+----+    +-----+------+    +-------+-------+    +------+-----+    +----+----+
    |               |                   |                   |                |
    | create_test() |                   |                   |                |
    +-------------->|                   |                   |                |
    |               | create_test()     |                   |                |
    |               +------------------>|                   |                |
    |               |                   |                   |                |
    |               |    test_id        |                   |                |
    |               |<------------------+                   |                |
    |   test_id     |                   |                   |                |
    |<--------------+                   |                   |                |
    |               |                   |                   |                |
    | run_test(test_id)                 |                   |                |
    +-------------->|                   |                   |                |
    |               | run_test(test_id) |                   |                |
    |               +------------------>|                   |                |
    |               |                   |                   |                |
    |               |     run_id        |                   |                |
    |               |<------------------+                   |                |
    |    run_id     |                   |                   |                |
    |<--------------+                   |                   |                |
    |               |                   |                   |                |
    | get_status(test_id, run_id)       |                   |                |
    +-------------->|                   |                   |                |
    |               | get_status()      |                   |                |
    |               +------------------>|                   |                |
    |               |                   |                   |                |
    |               |     status        |                   |                |
    |               |<------------------+                   |                |
    |    status     |                   |                   |                |
    |<--------------+                   |                   |                |
    |               |                   |                   |                |
    | get_results(test_id, run_id)      |                   |                |
    +------------------------------------+------------------>                |
    |               |                   |                   |                |
    |               |                   | get_results()     |                |
    |               |                   |<------------------+                |
    |               |                   |                   |                |
    |               |                   |   results         |                |
    |               |                   +------------------>|                |
    |               |                   |                   |                |
    |               |                   |                   | generate_report|
    |               |                   |                   +--------------->|
    |               |                   |                   |                |
    |               |                   |                   |    report      |
    |               |                   |                   |<---------------+
    |    report     |                   |                   |                |
    |<------------------------------------+----------------+                |
    |               |                   |                   |                |
+---+----+    +-----+------+    +-------+-------+    +------+-----+    +----+----+
| Client |    | TestBuilder|    | BreakingPoint |    | Analyzer   |    | Report  |
|        |    |            |    | API           |    |            |    | Generator|
+--------+    +------------+    +---------------+    +------------+    +---------+
```

## Data Flow Diagram: Analyzer Component

This diagram illustrates the flow of data through the analyzer component:

```
                              +--------------------+
                              |                    |
                              | Breaking Point API |
                              |                    |
                              +----------+---------+
                                         |
                                         | Raw Test Results
                                         v
+--------------------+        +----------+---------+
|                    |        |                    |
| Test Summary       +<-------+  TestResultAnalyzer|
| Extraction         |        |                    |
|                    |        +--+----------+------+
+--------------------+           |          |
       |                         |          |
       | Metrics                 |          |
       v                         |          |
+------+-----------+             |          |
|                  |             |          |
| Metric           |             |          |
| Comparison       +<------------+          |
|                  |                        |
+------+-----------+                        |
       |                                    |
       | Comparison Results                 |
       v                                    |
+------+-----------+      +-----------------v----+
|                  |      |                      |
| Report           |      | Chart                |
| Generation       |      | Generation           |
|                  |      |                      |
+------+-----------+      +----------+-----------+
       |                             |
       v                             v
+------+-----------+      +----------+-----------+
|                  |      |                      |
| HTML/CSV/PDF     |      | PNG/SVG              |
| Reports          |      | Charts               |
|                  |      |                      |
+------------------+      +----------------------+
```

## Modular Architecture of Analyzer Component

This diagram shows the modular design of the analyzer component, emphasizing the separation of concerns:

```
+--------------------------------------------------------+
|                                                        |
|                      analyzer.py                       |
|         (High-level functions and integration)         |
|                                                        |
+--------------------------------------------------------+
                              |
                              | Uses
                              v
+--------------------------------------------------------+
|                                                        |
|                       core.py                          |
|           (TestResultAnalyzer implementation)          |
|                                                        |
+--------------------------------------------------------+
        ^                   ^                   ^
        |                   |                   |
        | Uses              | Uses              | Uses
        |                   |                   |
+-------+---------+ +-------+---------+ +-------+---------+
|                 | |                 | |                 |
| Report          | | Chart           | | Result          |
| Generation      | | Generation      | | Processing      |
| Modules         | | Modules         | | Functionality   |
|                 | |                 | |                 |
+-----------------+ +-----------------+ +-----------------+
        |                   |
        v                   v
+-----------------+ +-----------------+
|                 | |                 |
| Specialized     | | Specialized     |
| Report Types    | | Chart Types     |
|                 | |                 |
+-----------------+ +-----------------+
```

## Test Type Processing Flow

This diagram illustrates how different test types are processed by the analyzer:

```
                      +---------------------+
                      |                     |
                      | Raw Test Results    |
                      |                     |
                      +----------+----------+
                                 |
                                 v
                      +----------+----------+
                      |                     |
                      | Test Type Detection |
                      |                     |
                      +----------+----------+
                                 |
                 +---------------+----------------+
                 |                                |
                 v                                v
       +---------+---------+           +---------+---------+
       |                   |           |                   |
       | Strike Test       |           | AppSim/ClientSim  |
       | Processing        |           | Processing        |
       |                   |           |                   |
       +---------+---------+           +---------+---------+
                 |                                |
    +------------+-------------+     +------------+-------------+
    |            |             |     |            |             |
    v            v             v     v            v             v
+---+---+    +---+---+    +----+--+  +---+---+   +---+---+   +---+---+
|       |    |       |    |       |  |       |   |       |   |       |
|Security|   |Detailed|   |Compli-|  |Standard|  |Detailed|  |Exec.  |
|Report  |   |Security|   |ance   |  |Report  |  |Perf.   |  |Report |
|       |    |Report  |   |Report |  |       |   |Report  |   |       |
+-------+    +-------+    +-------+  +-------+   +-------+   +-------+
```

These architectural diagrams provide visual representations of the Breaking Point MCP Agent's structure and functionality, making it easier to understand how the components interact and how data flows through the system.
