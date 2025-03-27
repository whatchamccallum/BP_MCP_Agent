# Installation Guide

This guide provides instructions for installing and setting up the Breaking Point MCP Agent.

## Prerequisites

Before installing the BP MCP Agent, ensure you have the following prerequisites:

- Python 3.7 or higher
- Access to an Ixia Breaking Point system with API capabilities
- Appropriate credentials for the Breaking Point system
- Claude Desktop AI with agent support

## Installation Steps

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/BP_MCP_Agent.git
cd BP_MCP_Agent
```

### 2. Create a Virtual Environment (Optional but Recommended)

```bash
# For Windows
python -m venv venv
venv\Scripts\activate

# For macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

The requirements.txt file includes the following key dependencies:

```
requests>=2.28.0
matplotlib>=3.5.0
pandas>=1.3.0
numpy>=1.21.0
```

### 4. Configuration

Create a configuration file named `bp_config.ini` in the root directory with your Breaking Point system information:

```ini
[BREAKING_POINT]
host = your-bp-system-ip
username = your-username
password = your-password
api_port = 443  # Default HTTPS port
verify_ssl = true  # Set to false if using self-signed certificates
```

### 5. Verify Installation

Run the verification script to ensure the installation is working correctly:

```bash
python -m tests.verify_installation
```

If the installation is successful, you should see output confirming the connection to your Breaking Point system.

## Troubleshooting

### Common Issues

#### Connection Problems

If you encounter connection issues:

1. Verify your Breaking Point system is reachable from your network
2. Check your credentials in the configuration file
3. If using self-signed certificates, set `verify_ssl = false` in the configuration file

#### Import Errors

If you see import errors:

1. Ensure you're running the script from the project root directory
2. Verify that all dependencies were installed correctly
3. Make sure you're using the correct Python environment if using virtual environments

### Getting Help

If you continue to experience issues:

1. Check the [GitHub Issues](https://github.com/yourusername/BP_MCP_Agent/issues) for similar problems
2. Create a new issue with detailed information about your problem

## Next Steps

After installation, refer to the [Usage Guide](usage_guide.md) to learn how to use the Breaking Point MCP Agent.
