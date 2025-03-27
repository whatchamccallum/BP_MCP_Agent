# Breaking Point MCP Agent Troubleshooting Guide

This guide helps troubleshoot common issues with the Breaking Point MCP Agent.

## Error Codes Reference

The agent uses standardized error codes to help identify and troubleshoot issues:

| Error Code | Description | Possible Solutions |
|------------|-------------|-------------------|
| `API_ERROR` | General API communication error | Check network connectivity and Breaking Point system status |
| `AUTH_ERROR` | Authentication failure | Verify credentials and check if account is locked |
| `NETWORK_ERROR` | Network connection issue | Check network connectivity and firewall settings |
| `TIMEOUT_ERROR` | Request timeout | Increase timeout in config or check system load |
| `TEST_CREATION_ERROR` | Failed to create test | Check test configuration for errors |
| `TEST_EXECUTION_ERROR` | Test execution failed | Verify test settings and system resources |
| `TEST_RESULT_ERROR` | Failed to retrieve test results | Check if test completed successfully |
| `VALIDATION_ERROR` | Input validation failure | Correct the invalid parameters |
| `CONFIG_ERROR` | Configuration error | Check configuration file for valid settings |
| `REPORT_ERROR` | Report generation failure | Check output directory permissions |
| `CHART_ERROR` | Chart generation failure | Verify matplotlib is correctly installed |
| `RESOURCE_NOT_FOUND` | Requested resource not found | Verify resource ID exists |
| `CACHE_ERROR` | Cache operation failure | Check cache directory permissions |
| `PLUGIN_ERROR` | Plugin operation failure | Verify plugin is compatible |
| `NO_RUN_ID` | No run ID returned when starting test | Check if test exists and can be run |

## Common Issues and Solutions

### Connection Problems

**Symptom:** `NETWORK_ERROR` or `TIMEOUT_ERROR` when connecting to Breaking Point

**Possible causes:**
- Breaking Point system is not reachable
- Network firewall is blocking connections
- Breaking Point system is overloaded

**Solutions:**
1. Verify the host address in the configuration
2. Check network connectivity (ping the Breaking Point system)
3. Ensure firewall allows HTTPS connections to the Breaking Point system
4. Try increasing the timeout in the configuration
5. Contact system administrator to check Breaking Point system status

### Authentication Issues

**Symptom:** `AUTH_ERROR` when connecting to Breaking Point

**Possible causes:**
- Incorrect username or password
- Account locked due to multiple failed login attempts
- Authentication token expired

**Solutions:**
1. Verify credentials in environment variables or configuration
2. Check if account is locked on the Breaking Point system
3. Try logging in through the Breaking Point web interface
4. Contact system administrator for account verification

### Test Execution Problems

**Symptom:** `TEST_EXECUTION_ERROR` when running a test

**Possible causes:**
- Test configuration is invalid
- Required resources are not available
- Breaking Point system is in use by others
- System lacks sufficient resources

**Solutions:**
1. Verify test configuration and parameters
2. Check if required ports/interfaces are available
3. Verify Breaking Point system resources
4. Try running a simpler test to verify basic functionality

### Results Retrieval Issues

**Symptom:** `TEST_RESULT_ERROR` when getting test results

**Possible causes:**
- Test did not complete successfully
- Results were deleted or expired
- API permissions issue

**Solutions:**
1. Verify test completed successfully (not in "running" or "error" state)
2. Check if results are available in Breaking Point web interface
3. Verify user has permissions to access test results
4. Try running the test again

### Report Generation Problems

**Symptom:** `REPORT_ERROR` or `CHART_ERROR` when generating reports

**Possible causes:**
- Missing required data
- Output directory permissions
- Missing Python dependencies

**Solutions:**
1. Verify test completed successfully with valid results
2. Check permissions on output directory
3. Ensure all required Python libraries are installed (especially matplotlib)
4. Try generating a different report type

### Cache Issues

**Symptom:** `CACHE_ERROR` when using the cache

**Possible causes:**
- Cache directory permissions
- Disk space issues
- Corrupted cache files

**Solutions:**
1. Check permissions on cache directory
2. Verify sufficient disk space
3. Try clearing the cache (`bp-agent cache clear`)
4. Disable caching temporarily if needed

## Logging

The agent provides detailed logging to help diagnose issues. By default, logs are written to `~/.bp_agent/logs/agent.log`.

### Log Levels

- `ERROR`: Critical issues preventing operation
- `WARNING`: Non-critical issues that should be reviewed
- `INFO`: General operational information
- `DEBUG`: Detailed information for troubleshooting

### Enabling Debug Logging

To enable more detailed logging, use the `--log-level DEBUG` option:

```
bp-agent --log-level DEBUG [command]
```

Alternatively, set the log level in the configuration file:

```yaml
logging:
  level: DEBUG
```

### Common Log Patterns

When troubleshooting, look for these patterns in the logs:

1. **Connection issues** will show network errors or timeouts
2. **Authentication issues** will show login failures
3. **API errors** will include HTTP status codes and response details
4. **Test execution issues** will show test state transitions
5. **Cache errors** will indicate file access problems

## Recovery Strategies

The agent implements several automatic recovery strategies:

1. **Automatic retries** for transient network issues
2. **Exponential backoff** to handle rate limiting
3. **Session recovery** for authentication issues
4. **Cache self-healing** for corrupted cache files

If automatic recovery fails, try these manual steps:

1. Clear the cache (`bp-agent cache clear`)
2. Verify configuration (`bp-agent init --force`)
3. Check system connectivity and resources
4. Restart the operation with debug logging enabled

## Contacting Support

If you cannot resolve an issue using this guide, gather the following information:

1. Full logs with `--log-level DEBUG` enabled
2. System information (OS, Python version)
3. Configuration file (with credentials removed)
4. Exact command that triggered the error
5. Error code and message

Then contact support with these details for further assistance.
