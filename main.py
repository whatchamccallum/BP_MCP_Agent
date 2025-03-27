#!/usr/bin/env python
"""
Breaking Point MCP Agent CLI
Command-line interface for Breaking Point MCP Agent.
"""

import os
import sys
import logging
import argparse
import traceback
from typing import Dict, List, Optional, Any, Tuple

from src.config import get_config
from src.init import initialize
from src.api import create_api
from src.cache import get_cache
from src import __version__
from src.exceptions import (
    BPError, 
    APIError, 
    AuthenticationError, 
    TestError, 
    ValidationError,
    ConfigurationError,
    format_error_for_user,
    format_error_for_logging
)
from src.error_handler import safe_execute

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
logger = logging.getLogger("BPAgent.CLI")

def parse_args() -> argparse.Namespace:
    """Parse command line arguments
    
    Returns:
        argparse.Namespace: Parsed arguments
    """
    parser = argparse.ArgumentParser(description="Breaking Point MCP Agent")
    
    # Global options
    parser.add_argument("--version", action="version", version=f"Breaking Point MCP Agent v{__version__}")
    parser.add_argument("--config", help="Path to configuration file")
    parser.add_argument("--host", help="Breaking Point host address")
    parser.add_argument("--username", help="Breaking Point username")
    parser.add_argument("--password", help="Breaking Point password")
    parser.add_argument("--verify-ssl", action="store_true", help="Verify SSL certificates")
    parser.add_argument("--log-level", choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
                      help="Logging level")
    
    # Subcommands
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # Initialize command
    init_parser = subparsers.add_parser("init", help="Initialize the agent")
    init_parser.add_argument("--force", action="store_true", help="Force reinitialization")
    
    # List tests command
    list_tests_parser = subparsers.add_parser("list-tests", help="List available tests")
    
    # Run test command
    run_test_parser = subparsers.add_parser("run-test", help="Run a test")
    run_test_parser.add_argument("test_id", help="Test ID")
    run_test_parser.add_argument("--wait", action="store_true", help="Wait for test completion")
    run_test_parser.add_argument("--timeout", type=int, default=3600, help="Timeout in seconds")
    
    # Get test results command
    results_parser = subparsers.add_parser("results", help="Get test results")
    results_parser.add_argument("test_id", help="Test ID")
    results_parser.add_argument("run_id", help="Run ID")
    results_parser.add_argument("--format", choices=["json", "summary", "report"], default="summary",
                             help="Output format")
    results_parser.add_argument("--report-type", choices=["standard", "executive", "detailed", "compliance"],
                             default="standard", help="Report type")
    results_parser.add_argument("--output-format", choices=["html", "csv", "pdf", "txt"],
                             default="html", help="Output format for report")
    results_parser.add_argument("--output-dir", default="./reports", help="Output directory for reports")
    results_parser.add_argument("--no-cache", action="store_true", help="Disable cache")
    
    # Compare results command
    compare_parser = subparsers.add_parser("compare", help="Compare test results")
    compare_parser.add_argument("test_id1", help="First test ID")
    compare_parser.add_argument("run_id1", help="First run ID")
    compare_parser.add_argument("test_id2", help="Second test ID")
    compare_parser.add_argument("run_id2", help="Second run ID")
    compare_parser.add_argument("--chart-type", choices=["throughput", "latency", "strikes", "transactions"],
                               default="throughput", help="Chart type for comparison")
    compare_parser.add_argument("--output-dir", default="./reports", help="Output directory for charts")
    compare_parser.add_argument("--no-cache", action="store_true", help="Disable cache")
    
    # Cache management commands
    cache_parser = subparsers.add_parser("cache", help="Cache management")
    cache_subparsers = cache_parser.add_subparsers(dest="cache_command", help="Cache command")
    
    # Cache stats command
    cache_stats_parser = cache_subparsers.add_parser("stats", help="Get cache statistics")
    
    # Cache clear command
    cache_clear_parser = cache_subparsers.add_parser("clear", help="Clear cache")
    
    # Cache cleanup command
    cache_cleanup_parser = cache_subparsers.add_parser("cleanup", help="Clean up expired cache entries")
    cache_cleanup_parser.add_argument("--max-age", type=int, help="Maximum age in seconds")
    
    return parser.parse_args()

def main() -> int:
    """Main entry point
    
    Returns:
        int: Exit code
    """
    try:
        # Parse arguments
        args = parse_args()
        
        # Setup logging
        log_level = args.log_level or "INFO"
        logging.basicConfig(level=getattr(logging, log_level))
        
        # Initialize configuration
        try:
            initialize(args.config)
        except ConfigurationError as e:
            logger.error(f"Configuration error: {format_error_for_logging(e)}")
            print(f"Error: {format_error_for_user(e)}")
            return 1
        
        # Update configuration from command line arguments
        config = get_config()
        config.load_from_args(args)
        
        # Dispatch command
        if args.command == "init":
            return cmd_init(args)
        elif args.command == "list-tests":
            return cmd_list_tests(args)
        elif args.command == "run-test":
            return cmd_run_test(args)
        elif args.command == "results":
            return cmd_results(args)
        elif args.command == "compare":
            return cmd_compare(args)
        elif args.command == "cache":
            return cmd_cache(args)
        else:
            print("No command specified. Run with --help for usage information.")
            print("Use --help for available commands.")
            return 1
            
    except KeyboardInterrupt:
        print("\nOperation canceled by user.")
        return 130  # Standard exit code for SIGINT
        
    except BPError as e:
        # Handle our custom exceptions
        logger.error(f"Error: {format_error_for_logging(e)}")
        print(f"Error: {format_error_for_user(e)}")
        return 1
        
    except Exception as e:
        # Handle unexpected exceptions
        logger.error(f"Unexpected error: {e}")
        logger.debug(f"Traceback: {traceback.format_exc()}")
        print(f"An unexpected error occurred: {e}")
        print("This is likely a bug. Please report it with the details from the log.")
        return 2

def cmd_init(args: argparse.Namespace) -> int:
    """Initialize the agent
    
    Args:
        args: Command line arguments
        
    Returns:
        int: Exit code
    """
    print("Initializing Breaking Point MCP Agent...")
    
    if initialize(args.config, create_default_config=True):
        print("Initialization complete.")
        return 0
    else:
        print("Initialization failed.")
        return 1

def cmd_list_tests(args: argparse.Namespace) -> int:
    """List available tests
    
    Args:
        args: Command line arguments
        
    Returns:
        int: Exit code
    """
    try:
        print("Connecting to Breaking Point...")
        api = create_api(args.host, args.username, args.password)
        
        with api:
            print("Getting tests...")
            tests = api.get_tests()
            
            print(f"\nFound {len(tests)} tests:")
            for test in tests:
                test_id = test.get("id", "Unknown")
                test_name = test.get("name", "Unknown")
                test_type = test.get("type", "Unknown")
                print(f"  {test_id}: {test_name} ({test_type})")
            
            return 0
    except Exception as e:
        print(f"Error listing tests: {e}")
        return 1

def cmd_run_test(args: argparse.Namespace) -> int:
    """Run a test
    
    Args:
        args: Command line arguments
        
    Returns:
        int: Exit code
    """
    context_info = {
        "test_id": args.test_id,
        "wait_for_completion": args.wait,
        "timeout": args.timeout
    }
    
    def run_test_impl():
        print("Connecting to Breaking Point...")
        api = create_api(args.host, args.username, args.password)
        
        with api:
            print(f"Running test {args.test_id}...")
            result = api.run_test(args.test_id)
            run_id = result.get("runId")
            
            if not run_id:
                raise TestError(
                    "No run ID returned from API", 
                    test_id=args.test_id, 
                    error_code="NO_RUN_ID"
                )
                
            print(f"Test started with run ID: {run_id}")
            
            if args.wait:
                import time
                print("Waiting for test completion...")
                
                start_time = time.time()
                last_status = None
                progress_indicators = ["|", "/", "-", "\\"]
                progress_index = 0
                
                try:
                    while True:
                        # Check timeout
                        elapsed = time.time() - start_time
                        if elapsed > args.timeout:
                            print(f"\nTimeout after {elapsed:.1f} seconds, test still running")
                            print(f"You can check the status later with: bp-agent results {args.test_id} {run_id}")
                            return 2
                        
                        # Get test status
                        status = api.get_test_status(args.test_id, run_id)
                        
                        # Print status if changed
                        if status != last_status:
                            if last_status is not None:
                                # Clear progress indicator line
                                print("\r" + " " * 80 + "\r", end="")
                            print(f"Test status: {status}")
                            last_status = status
                        else:
                            # Show progress indicator
                            indicator = progress_indicators[progress_index]
                            progress_index = (progress_index + 1) % len(progress_indicators)
                            elapsed_str = f"{elapsed:.1f}s"
                            print(f"\rWaiting for completion {indicator} ({elapsed_str})", end="")
                        
                        # Check if test is complete
                        if status in ["completed", "stopped", "aborted", "failed"]:
                            # Clear progress indicator line
                            if status == last_status:
                                print("\r" + " " * 80 + "\r", end="")
                            break
                        
                        # Wait before checking again
                        time.sleep(5)
                finally:
                    # Ensure we return to a new line
                    print("")
                
                result_msg = "completed successfully" if status == "completed" else f"ended with status: {status}"
                print(f"Test {result_msg}")
                print(f"Run ID: {run_id}")
                print(f"To view results: bp-agent results {args.test_id} {run_id}")
            else:
                print(f"Test is running in the background.")
                print(f"Run ID: {run_id}")
                print(f"Check status with: bp-agent results {args.test_id} {run_id}")
            
            return 0
    
    # Execute with error handling
    return safe_execute(
        run_test_impl, 
        context_info, 
        TestError, 
        "TEST_RUN_ERROR"
    )

def cmd_results(args: argparse.Namespace) -> int:
    """Get test results
    
    Args:
        args: Command line arguments
        
    Returns:
        int: Exit code
    """
    try:
        print("Connecting to Breaking Point...")
        api = create_api(args.host, args.username, args.password)
        
        with api:
            print(f"Getting results for test {args.test_id}, run {args.run_id}...")
            
            if args.format == "json":
                # Get raw results
                results = api.get_test_results(args.test_id, args.run_id, use_cache=not args.no_cache)
                
                # Pretty print results
                import json
                print(json.dumps(results, indent=2))
                
            elif args.format == "summary":
                # Get results summary
                from src.analyzer import get_test_result_summary
                summary = get_test_result_summary(api, args.test_id, args.run_id, use_cache=not args.no_cache)
                
                # Print summary
                print(f"\nTest: {summary['testName']} ({summary['testType']})")
                print(f"Status: {summary['status']}")
                print(f"Duration: {summary['duration']} seconds")
                print(f"Start Time: {summary['startTime']}")
                print(f"End Time: {summary['endTime']}")
                
                # Print metrics
                print("\nMetrics:")
                if "throughput" in summary["metrics"]:
                    throughput = summary["metrics"]["throughput"]
                    print(f"  Throughput: {throughput['average']} {throughput['unit']} (avg), "
                         f"{throughput['maximum']} {throughput['unit']} (max)")
                
                if "latency" in summary["metrics"]:
                    latency = summary["metrics"]["latency"]
                    print(f"  Latency: {latency['average']} {latency['unit']} (avg), "
                         f"{latency['maximum']} {latency['unit']} (max)")
                
                if "strikes" in summary["metrics"]:
                    strikes = summary["metrics"]["strikes"]
                    print(f"  Strikes: {strikes['attempted']} attempted, {strikes['blocked']} blocked, "
                         f"{strikes['allowed']} allowed, {strikes['successRate']}% success rate")
                
                if "transactions" in summary["metrics"]:
                    transactions = summary["metrics"]["transactions"]
                    print(f"  Transactions: {transactions['attempted']} attempted, {transactions['successful']} successful, "
                         f"{transactions['failed']} failed, {transactions['successRate']}% success rate")
                
            elif args.format == "report":
                # Generate report
                from src.analyzer import generate_report
                output_dir = os.path.expanduser(args.output_dir)
                
                print(f"Generating {args.report_type} report in {args.output_format} format...")
                report_path = generate_report(
                    api, 
                    args.test_id, 
                    args.run_id, 
                    output_format=args.output_format,
                    report_type=args.report_type,
                    output_dir=output_dir
                )
                
                print(f"Report generated: {report_path}")
                
                # Generate charts
                from src.analyzer import generate_charts
                print("Generating charts...")
                chart_paths = generate_charts(api, args.test_id, args.run_id, output_dir=output_dir)
                
                print(f"Generated {len(chart_paths)} charts")
                for path in chart_paths:
                    print(f"  {path}")
            
            return 0
    except Exception as e:
        print(f"Error getting test results: {e}")
        return 1

def cmd_compare(args: argparse.Namespace) -> int:
    """Compare test results
    
    Args:
        args: Command line arguments
        
    Returns:
        int: Exit code
    """
    try:
        print("Connecting to Breaking Point...")
        api = create_api(args.host, args.username, args.password)
        
        with api:
            print(f"Comparing test {args.test_id1}, run {args.run_id1} with test {args.test_id2}, run {args.run_id2}...")
            
            # Compare results
            from src.analyzer import compare_test_results
            comparison = compare_test_results(
                api, 
                args.test_id1, args.run_id1, 
                args.test_id2, args.run_id2,
                use_cache=not args.no_cache
            )
            
            # Print comparison summary
            test1_name = comparison["test1"]["testName"]
            test2_name = comparison["test2"]["testName"]
            
            print(f"\nComparison: {test1_name} vs {test2_name}")
            
            # Print metrics comparison
            for metric_name, metric_data in comparison["metrics"].items():
                print(f"\n{metric_name.capitalize()} comparison:")
                
                # Get metric info
                test1_metric = metric_data["test1"]
                test2_metric = metric_data["test2"]
                diff = metric_data["difference"]
                
                if metric_name in ["throughput", "latency"]:
                    # Print performance metrics
                    test1_avg = test1_metric["average"]
                    test2_avg = test2_metric["average"]
                    avg_diff = diff["average"]
                    pct_diff = diff["percentage"]
                    unit = test1_metric.get("unit", "")
                    
                    print(f"  {test1_name}: {test1_avg} {unit} (avg)")
                    print(f"  {test2_name}: {test2_avg} {unit} (avg)")
                    print(f"  Difference: {avg_diff:+.2f} {unit} ({pct_diff:+.2f}%)")
                    
                elif metric_name in ["strikes", "transactions"]:
                    # Print success rate metrics
                    test1_rate = test1_metric["successRate"]
                    test2_rate = test2_metric["successRate"]
                    rate_diff = diff["successRate"]
                    
                    print(f"  {test1_name}: {test1_rate}% success rate")
                    print(f"  {test2_name}: {test2_rate}% success rate")
                    print(f"  Difference: {rate_diff:+.2f}%")
            
            # Generate comparison chart
            output_dir = os.path.expanduser(args.output_dir)
            
            from src.analyzer import compare_charts
            print(f"Generating {args.chart_type} comparison chart...")
            chart_path = compare_charts(
                api, 
                args.test_id1, args.run_id1, 
                args.test_id2, args.run_id2,
                args.chart_type,
                output_dir=output_dir
            )
            
            print(f"Comparison chart generated: {chart_path}")
            
            return 0
    except Exception as e:
        print(f"Error comparing test results: {e}")
        return 1

def cmd_cache(args: argparse.Namespace) -> int:
    """Cache management
    
    Args:
        args: Command line arguments
        
    Returns:
        int: Exit code
    """
    cache = get_cache()
    
    if args.cache_command == "stats":
        stats = cache.get_stats()
        print("\nCache Statistics:")
        print(f"  Directory: {stats['cache_dir']}")
        print(f"  TTL: {stats['ttl']} seconds")
        print(f"  Compression: {'enabled' if stats.get('compression', False) else 'disabled'}")
        print(f"  Entries: {stats['entry_count']}")
        print(f"  Size: {stats.get('size_human', '0 bytes')}")
        if stats['entry_count'] > 0:
            print(f"  Oldest entry: {stats.get('oldest_entry', 'Unknown')}")
            print(f"  Newest entry: {stats.get('newest_entry', 'Unknown')}")
            
    elif args.cache_command == "clear":
        count = cache.clear()
        print(f"Cleared {count} cache entries")
        
    elif args.cache_command == "cleanup":
        count = cache.cleanup(args.max_age)
        print(f"Cleaned up {count} expired cache entries")
        
    else:
        print("No cache command specified. Run with --help for usage information.")
        return 1
        
    return 0

if __name__ == "__main__":
    sys.exit(main())
