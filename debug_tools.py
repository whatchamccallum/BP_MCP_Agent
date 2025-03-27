"""
Debugging utilities for Breaking Point MCP Agent
Helps identify and diagnose issues with the agent
"""

import os
import sys
import json
import logging
import traceback
import importlib
import inspect
from typing import Dict, List, Any, Optional, Set

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from src.config import get_config
from src.init import initialize
from src.api import create_api, BreakingPointAPI
from src.exceptions import BPError

# Configure logging
logging.basicConfig(level=logging.DEBUG, 
                   format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
logger = logging.getLogger("BPAgent.Debug")

def check_environment():
    """Check environment for potential issues"""
    logger.info("Checking environment...")
    
    # Check Python version
    python_version = sys.version.split()[0]
    logger.info(f"Python version: {python_version}")
    major, minor, micro = map(int, python_version.split('.'))
    if major < 3 or (major == 3 and minor < 7):
        logger.error(f"Python version {python_version} is below minimum required (3.7)")
    
    # Check required packages
    required_packages = [
        'requests', 'aiohttp', 'matplotlib', 'pyyaml'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            importlib.import_module(package)
            logger.info(f"Package {package} is installed")
        except ImportError:
            logger.error(f"Required package {package} is not installed")
            missing_packages.append(package)
    
    # Check directories
    config = get_config()
    cache_dir = os.path.expanduser(config.get("cache", "dir", "~/.bp_agent/cache"))
    log_dir = os.path.dirname(os.path.expanduser(config.get("logging", "file", "~/.bp_agent/logs/agent.log")))
    
    dirs_to_check = [cache_dir, log_dir]
    for directory in dirs_to_check:
        if os.path.exists(directory):
            # Check write permissions
            if os.access(directory, os.W_OK):
                logger.info(f"Directory {directory} exists and is writable")
            else:
                logger.error(f"Directory {directory} exists but is not writable")
        else:
            logger.warning(f"Directory {directory} does not exist")
    
    # Return issues summary
    return {
        "python_version": python_version,
        "python_version_ok": not (major < 3 or (major == 3 and minor < 7)),
        "missing_packages": missing_packages,
        "directories": {d: os.path.exists(d) and os.access(d, os.W_OK) for d in dirs_to_check}
    }

def check_configuration():
    """Check configuration for potential issues"""
    logger.info("Checking configuration...")
    
    # Load configuration
    config = get_config()
    
    # Check required configuration values
    api_config = config.get_api_config()
    host = api_config.get("host")
    if not host or host == "breaking-point.example.com":
        logger.error(f"API host not configured or using default value: {host}")
    
    # Check credentials
    credentials = config.get_credentials()
    username = credentials.get("username")
    password = credentials.get("password")
    
    if not username or not password:
        logger.error("API credentials not configured")
    elif username == "admin" and password == "password":
        logger.warning("Using default credentials - this is insecure")
    
    # Check cache configuration
    cache_config = config.get_cache_config()
    if not cache_config.get("enabled", True):
        logger.warning("Cache is disabled - this may impact performance")
    
    # Check analyzer configuration
    analyzer_config = config.get_analyzer_config()
    plugin_dirs = analyzer_config.get("plugin_dirs", [])
    for plugin_dir in plugin_dirs:
        expanded_dir = os.path.expanduser(plugin_dir)
        if not os.path.exists(expanded_dir):
            logger.warning(f"Plugin directory does not exist: {plugin_dir}")
    
    # Return configuration summary
    return {
        "host_configured": bool(host) and host != "breaking-point.example.com",
        "credentials_configured": bool(username) and bool(password),
        "using_default_credentials": username == "admin" and password == "password",
        "cache_enabled": cache_config.get("enabled", True),
        "plugin_dirs": {dir: os.path.exists(os.path.expanduser(dir)) for dir in plugin_dirs}
    }

def validate_api_connectivity():
    """Test API connectivity"""
    logger.info("Testing API connectivity...")
    
    # Get configuration
    config = get_config()
    api_config = config.get_api_config()
    credentials = config.get_credentials()
    
    # Check if we have configuration to test
    if not api_config.get("host") or not credentials.get("username") or not credentials.get("password"):
        logger.error("Cannot test API connectivity - missing configuration")
        return {
            "connectivity_tested": False,
            "reason": "Missing configuration"
        }
    
    # Create API instance
    api = create_api()
    
    # Test connection
    try:
        api.login()
        logger.info("API connection successful")
        
        # Test basic API operations
        try:
            tests = api.get_tests()
            logger.info(f"Successfully retrieved {len(tests)} tests")
            operation_results = {
                "get_tests": True,
                "test_count": len(tests)
            }
        except BPError as e:
            logger.error(f"Error retrieving tests: {e}")
            operation_results = {
                "get_tests": False,
                "error": str(e)
            }
        
        # Clean up
        api.logout()
        
        return {
            "connectivity_tested": True,
            "connection_successful": True,
            "operations": operation_results
        }
        
    except BPError as e:
        logger.error(f"API connection failed: {e}")
        return {
            "connectivity_tested": True,
            "connection_successful": False,
            "error": str(e)
        }
    except Exception as e:
        logger.error(f"Unexpected error testing API connectivity: {e}")
        logger.debug(traceback.format_exc())
        return {
            "connectivity_tested": True,
            "connection_successful": False,
            "error": str(e),
            "traceback": traceback.format_exc()
        }

def check_async_api():
    """Test asynchronous API functionality"""
    logger.info("Testing asynchronous API...")
    
    try:
        # Import async modules
        from src.api_async import AsyncBreakingPointAPI
        import asyncio
        
        # Define async test function
        async def test_async_api():
            # Get configuration
            config = get_config()
            api_config = config.get_api_config()
            credentials = config.get_credentials()
            
            # Check if we have configuration to test
            if not api_config.get("host") or not credentials.get("username") or not credentials.get("password"):
                logger.error("Cannot test async API - missing configuration")
                return {
                    "async_tested": False,
                    "reason": "Missing configuration"
                }
            
            # Create API instance
            api = AsyncBreakingPointAPI(
                api_config.get("host"),
                credentials.get("username"),
                credentials.get("password"),
                api_config.get("verify_ssl", False)
            )
            
            # Test connection
            try:
                await api.login()
                logger.info("Async API connection successful")
                
                # Test basic API operations
                try:
                    tests = await api.get_tests()
                    logger.info(f"Successfully retrieved {len(tests)} tests using async API")
                    operation_results = {
                        "get_tests": True,
                        "test_count": len(tests)
                    }
                except BPError as e:
                    logger.error(f"Error retrieving tests with async API: {e}")
                    operation_results = {
                        "get_tests": False,
                        "error": str(e)
                    }
                
                # Clean up
                await api.logout()
                
                return {
                    "async_tested": True,
                    "connection_successful": True,
                    "operations": operation_results
                }
                
            except BPError as e:
                logger.error(f"Async API connection failed: {e}")
                return {
                    "async_tested": True,
                    "connection_successful": False,
                    "error": str(e)
                }
            except Exception as e:
                logger.error(f"Unexpected error testing async API: {e}")
                logger.debug(traceback.format_exc())
                return {
                    "async_tested": True,
                    "connection_successful": False,
                    "error": str(e),
                    "traceback": traceback.format_exc()
                }
        
        # Run the async test
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(test_async_api())
        
    except ImportError as e:
        logger.error(f"Could not import async modules: {e}")
        return {
            "async_tested": False,
            "reason": f"Import error: {e}"
        }
    except Exception as e:
        logger.error(f"Unexpected error setting up async test: {e}")
        logger.debug(traceback.format_exc())
        return {
            "async_tested": False,
            "reason": f"Setup error: {e}",
            "traceback": traceback.format_exc()
        }

def check_plugin_system():
    """Test plugin system functionality"""
    logger.info("Testing plugin system...")
    
    try:
        # Import plugin modules
        from src.analyzer.plugins.registry import get_plugin_manager, discover_plugins
        
        # Get plugin manager
        manager = get_plugin_manager()
        
        # Check built-in plugins
        report_generators = list(manager.report_generators.keys())
        chart_generators = list(manager.chart_generators.keys())
        
        logger.info(f"Found {len(report_generators)} report generators: {', '.join(report_generators)}")
        logger.info(f"Found {len(chart_generators)} chart generators: {', '.join(chart_generators)}")
        
        # Discover additional plugins
        config = get_config()
        analyzer_config = config.get_analyzer_config()
        plugin_dirs = analyzer_config.get("plugin_dirs", [])
        
        if plugin_dirs:
            # Try to discover plugins
            before_count = len(manager.report_generators) + len(manager.chart_generators)
            
            try:
                discover_plugins(plugin_dirs)
                after_count = len(manager.report_generators) + len(manager.chart_generators)
                new_plugins = after_count - before_count
                
                logger.info(f"Discovered {new_plugins} additional plugins")
                
                # Get updated plugin lists
                report_generators = list(manager.report_generators.keys())
                chart_generators = list(manager.chart_generators.keys())
            except Exception as e:
                logger.error(f"Error discovering plugins: {e}")
                logger.debug(traceback.format_exc())
        
        # Return plugin system summary
        return {
            "plugin_system_available": True,
            "report_generators": report_generators,
            "chart_generators": chart_generators,
            "plugin_dirs_configured": plugin_dirs,
            "plugin_count": len(report_generators) + len(chart_generators)
        }
    
    except ImportError as e:
        logger.error(f"Could not import plugin modules: {e}")
        return {
            "plugin_system_available": False,
            "reason": f"Import error: {e}"
        }
    except Exception as e:
        logger.error(f"Unexpected error checking plugin system: {e}")
        logger.debug(traceback.format_exc())
        return {
            "plugin_system_available": False,
            "reason": f"Error: {e}",
            "traceback": traceback.format_exc()
        }

def check_cache_system():
    """Test cache system functionality"""
    logger.info("Testing cache system...")
    
    try:
        # Import cache module
        from src.cache import get_cache
        
        # Get cache instance
        cache = get_cache()
        
        # Get cache statistics
        stats = cache.get_stats()
        logger.info(f"Cache statistics: {stats}")
        
        # Test basic cache operations
        test_key = "debug-test-id"
        test_run = "debug-run-id"
        test_data = {"test": "data", "timestamp": str(datetime.now())}
        
        # Write to cache
        write_success = cache.set(test_key, test_run, test_data)
        logger.info(f"Cache write {'successful' if write_success else 'failed'}")
        
        # Read from cache
        read_data = cache.get(test_key, test_run)
        read_success = read_data is not None
        data_match = read_data == test_data if read_success else False
        
        logger.info(f"Cache read {'successful' if read_success else 'failed'}")
        if read_success:
            logger.info(f"Data match: {data_match}")
        
        # Clean up
        cache.invalidate(test_key, test_run)
        
        # Return cache system summary
        return {
            "cache_system_available": True,
            "stats": stats,
            "write_test": write_success,
            "read_test": read_success,
            "data_integrity": data_match
        }
    
    except ImportError as e:
        logger.error(f"Could not import cache module: {e}")
        return {
            "cache_system_available": False,
            "reason": f"Import error: {e}"
        }
    except Exception as e:
        logger.error(f"Unexpected error checking cache system: {e}")
        logger.debug(traceback.format_exc())
        return {
            "cache_system_available": False,
            "reason": f"Error: {e}",
            "traceback": traceback.format_exc()
        }

def check_error_handling():
    """Test error handling system"""
    logger.info("Testing error handling system...")
    
    try:
        # Import error handling modules
        from src.exceptions import (
            BPError, APIError, NetworkError, TestError, 
            ValidationError, format_error_for_user
        )
        from src.error_handler import retry_with_backoff, ErrorContext
        
        # Check exception inheritance
        exception_types = {
            "BPError": BPError,
            "APIError": APIError,
            "NetworkError": NetworkError,
            "TestError": TestError,
            "ValidationError": ValidationError
        }
        
        inheritance_check = {}
        for name, exc_type in exception_types.items():
            if name != "BPError":
                inheritance_check[name] = issubclass(exc_type, BPError)
                logger.info(f"Exception {name} is{'' if inheritance_check[name] else ' not'} a subclass of BPError")
        
        # Test error message formatting
        error = APIError("Test error message", status_code=500, endpoint="test/endpoint")
        user_message = format_error_for_user(error)
        logger.info(f"User message: {user_message}")
        
        # Test retry decorator
        retry_counter = [0]
        
        @retry_with_backoff()
        def test_retry_function():
            retry_counter[0] += 1
            if retry_counter[0] < 3:
                raise NetworkError("Test network error", "test/endpoint", False)
            return "Success after retries"
        
        try:
            result = test_retry_function()
            logger.info(f"Retry test result: {result} after {retry_counter[0]} attempts")
            retry_test_result = {
                "success": True,
                "attempts": retry_counter[0],
                "result": result
            }
        except Exception as e:
            logger.error(f"Retry test failed: {e}")
            retry_test_result = {
                "success": False,
                "attempts": retry_counter[0],
                "error": str(e)
            }
        
        # Test error context
        context_test_result = {}
        try:
            with ErrorContext({"test_context": "value"}, APIError, "TEST_ERROR"):
                # Intentionally raise an exception
                raise ValueError("Test error inside context")
        except Exception as e:
            logger.info(f"Error context test caught: {type(e).__name__}: {e}")
            context_test_result = {
                "exception_type": type(e).__name__,
                "is_bp_error": isinstance(e, BPError),
                "message": str(e)
            }
        
        # Return error handling summary
        return {
            "error_system_available": True,
            "inheritance_check": inheritance_check,
            "user_message_test": user_message is not None,
            "retry_test": retry_test_result,
            "context_test": context_test_result
        }
    
    except ImportError as e:
        logger.error(f"Could not import error handling modules: {e}")
        return {
            "error_system_available": False,
            "reason": f"Import error: {e}"
        }
    except Exception as e:
        logger.error(f"Unexpected error checking error handling system: {e}")
        logger.debug(traceback.format_exc())
        return {
            "error_system_available": False,
            "reason": f"Error: {e}",
            "traceback": traceback.format_exc()
        }

def main():
    """Run all debug checks"""
    from datetime import datetime
    print("\n================================")
    print("Breaking Point MCP Agent Debugger")
    print("================================\n")
    
    print("Starting debug checks at", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("\nThis will check various components of the MCP Agent.")
    print("Some tests may fail if you haven't configured the agent yet.\n")
    
    # Initialize configuration
    try:
        initialize()
    except Exception as e:
        print(f"Error initializing: {e}")
    
    # Run all checks
    results = {
        "environment": check_environment(),
        "configuration": check_configuration(),
        "api_connectivity": validate_api_connectivity(),
        "async_api": check_async_api(),
        "plugin_system": check_plugin_system(),
        "cache_system": check_cache_system(),
        "error_handling": check_error_handling()
    }
    
    # Save results to file
    output_file = "debug_results.json"
    with open(output_file, "w") as f:
        json.dump(results, f, indent=2)
    
    print("\nDebug checks completed.")
    print(f"Detailed results have been saved to {output_file}")
    
    # Print summary
    print("\nSummary:")
    print(f"- Environment: {'OK' if results['environment']['python_version_ok'] and not results['environment']['missing_packages'] else 'Issues found'}")
    print(f"- Configuration: {'OK' if results['configuration']['host_configured'] and results['configuration']['credentials_configured'] else 'Issues found'}")
    print(f"- API Connectivity: {'OK' if results['api_connectivity'].get('connection_successful', False) else 'Issues found'}")
    print(f"- Async API: {'OK' if results['async_api'].get('connection_successful', False) else 'Issues found'}")
    print(f"- Plugin System: {'OK' if results['plugin_system'].get('plugin_system_available', False) else 'Issues found'}")
    print(f"- Cache System: {'OK' if results['cache_system'].get('cache_system_available', False) and results['cache_system'].get('write_test', False) else 'Issues found'}")
    print(f"- Error Handling: {'OK' if results['error_handling'].get('error_system_available', False) else 'Issues found'}")
    
    print("\nFor detailed information, check the logs and the debug_results.json file.")

if __name__ == "__main__":
    from datetime import datetime
    main()
