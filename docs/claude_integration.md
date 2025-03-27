# Configuring Claude Desktop AI with BP_MCP_Agent

This guide provides instructions for configuring Claude Desktop AI to work with the Breaking Point MCP Agent.

## Prerequisites

- Successfully installed BP_MCP_Agent following the [Installation Guide](installation_guide.md)
- Claude Desktop AI installed on your machine
- Access to a Breaking Point system with API capabilities
- Proper credentials for the Breaking Point system

## Configuration Steps

### 1. Create a Configuration File

Create a `config.yaml` file in the root directory of the BP_MCP_Agent project using the example file as a template:

```bash
# For Windows
copy config.yaml.example config.yaml

# For macOS/Linux
cp config.yaml.example config.yaml
```

Edit the configuration file with your Breaking Point system details:

```yaml
# API Connection Settings
api:
  host: your-breaking-point-system
  timeout: 60
  verify_ssl: false  # Set to true if using valid SSL certificates
  retries: 3
  retry_delay: 5

# Credentials (using environment variables is recommended for production)
credentials:
  username: your_username
  password: your_password
```

### 2. Set Up Python Environment

It's highly recommended to use the virtual environment created during installation. You'll need to ensure Claude can access this environment when executing the agent.

### 3. Configure the Wrapper Scripts

Two wrapper scripts are provided with the BP_MCP_Agent to ensure proper JSON formatting when communicating with Claude Desktop AI:

#### Windows Script (run_bp_agent.bat)

Edit the `run_bp_agent.bat` file in the BP_MCP_Agent directory to update the path to your virtual environment:

```batch
REM Activate the virtual environment
call C:\path\to\your\venv\Scripts\activate.bat
```

Change this line to point to your actual virtual environment path.

#### macOS/Linux Script (run_bp_agent.sh)

Edit the `run_bp_agent.sh` file in the BP_MCP_Agent directory to update the path to your virtual environment:

```bash
# Activate the virtual environment
source /path/to/your/venv/bin/activate
```

Change this line to point to your actual virtual environment path.

Make the script executable:
```bash
chmod +x run_bp_agent.sh
```

### 4. Configure Claude Desktop AI

1. Open Claude Desktop AI
2. Navigate to Settings (usually accessed through the gear/cog icon)
3. Select the "Agents" or "Extensions" section
4. Click "Add Agent" or "Add Extension"
5. Fill in the following details:

   - **Name**: Breaking Point MCP Agent
   - **Description**: A Management Control Protocol agent for Ixia Breaking Point to create, control, monitor, and analyze traffic test scenarios
   - **Command**:
     - Windows: `C:\path\to\BP_MCP_Agent\run_bp_agent.bat`
     - macOS/Linux: `/path/to/BP_MCP_Agent/run_bp_agent.sh`
   - **Working Directory**: Full path to your BP_MCP_Agent directory

6. (Optional) Set environment variables:
   - `BP_AGENT_API_HOST`: Your Breaking Point system hostname or IP
   - `BP_AGENT_USERNAME`: Your Breaking Point username
   - `BP_AGENT_PASSWORD`: Your Breaking Point password

   Note: If you've set credentials in the config.yaml file, these environment variables are optional.

7. Save the agent configuration

### 5. Verify the Integration

1. In Claude Desktop AI, start a new conversation
2. Test the agent with a basic command such as:
   - "List available tests on my Breaking Point system"
   - "Get information about the Breaking Point configuration"

3. If the agent is properly configured, Claude should invoke it and return the requested information

## Troubleshooting

If you encounter issues with the Claude integration:

1. **JSON Formatting Issues**:
   - The main script is designed to wrap all output in a JSON structure. If you see errors like "Unexpected token", make sure you're using the wrapper scripts.

2. **Check Environment Setup**:
   - Verify your Python virtual environment is correctly activated by the wrapper script
   - Ensure all required dependencies are installed in the environment

3. **Validate Breaking Point Connectivity**:
   Test connectivity to your Breaking Point system:
   ```bash
   # Activate your virtual environment first
   python -m tests.verify_installation
   ```

4. **Check Logs**:
   - Review the BP_MCP_Agent logs (found in the directory specified in config.yaml)
   - Check Claude Desktop logs for any agent execution errors

5. **Test the Agent Directly**:
   Run the agent manually to verify it works outside of Claude:
   ```bash
   # For Windows
   run_bp_agent.bat list-tests
   
   # For macOS/Linux
   ./run_bp_agent.sh list-tests
   ```
   The output should be in valid JSON format with the result wrapped in a "result" key.

6. **Common Issues**:
   - **Permission Errors**: Ensure the wrapper script has execute permissions
   - **Path Issues**: Verify all paths in the wrapper script are absolute and correct
   - **SSL Certificate Issues**: If your Breaking Point system uses a self-signed certificate, set `verify_ssl: false` in config.yaml

## Using the Agent with Claude

Once configured, you can ask Claude to perform various operations with the Breaking Point system:

- "Run a strike test against my network configuration"
- "Generate a security report for test X with run ID Y"
- "Compare performance between two test runs"
- "List available test configurations on my Breaking Point system"
- "Create a new application simulation test"

Claude will use the BP_MCP_Agent to communicate with the Breaking Point system and return the results in a conversational format.
