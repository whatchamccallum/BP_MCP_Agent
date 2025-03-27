"""
Command Line Interface for the Breaking Point MCP Agent
This module provides a command-line interface for the Breaking Point MCP Agent.
"""

import argparse
import sys
import os
import logging
from typing import List, Optional

from .api import BreakingPointAPI
from .analyzer import (
    get_test_result_summary,
    generate_report,
    generate_charts,
    compare_test_results,
    compare_charts,
    batch_process_tests
)
from .test_builder import TestBuilder
from .topology import NetworkTopology
from .superflow import SuperFlowManager
from .utils import configure_logging, load_config
from .constants import (
    VALID_REPORT_TYPES,
    VALID_OUTPUT_FORMATS,
    VALID_CHART_TYPES,
    DEFAULT_OUTPUT_DIR,
    DEFAULT_REPORTS_DIR,
    DEFAULT_CHARTS_DIR
)
from .exceptions import APIError, TestResultError, ReportError, ChartError, ValidationError

logger = logging.getLogger("BPAgent.CLI")

def list_tests_command(args):
    """List all available tests"""
    try:
        bp_api = BreakingPointAPI(args.host, args.username, args.password)
        bp_api.login()
        
        tests = bp_api.get_tests()
        
        print(f"Found {len(tests)} tests:")
        for test in tests:
            print(f"  - {test.get('id', 'N/A')}: {test.get('name', 'Unnamed')} ({test.get('type', 'Unknown')})")
            
        bp_api.logout()
        return 0
    except Exception as e:
        logger.error(f"Error listing tests: {str(e)}")
        return 1

def run_test_command(args):
    """Run a test"""
    try:
        bp_api = BreakingPointAPI(args.host, args.username, args.password)
        bp_api.login()
        
        result = bp_api.run_test(args.test_id)
        
        print(f"Test {args.test_id} started with run ID: {result.get('runId', 'Unknown')}")
        
        bp_api.logout()
        return 0
    except Exception as e:
        logger.error(f"Error running test: {str(e)}")
        return 1

def generate_report_command(args):
    """Generate a report for a test run"""
    try:
        bp_api = BreakingPointAPI(args.host, args.username, args.password)
        bp_api.login()
        
        # Ensure output directory exists
        os.makedirs(args.output_dir, exist_ok=True)
        
        report_path = generate_report(
            bp_api, 
            args.test_id, 
            args.run_id, 
            args.format, 
            args.type, 
            args.output_dir
        )
        
        print(f"Report generated: {report_path}")
        
        bp_api.logout()
        return 0
    except Exception as e:
        logger.error(f"Error generating report: {str(e)}")
        return 1

def generate_charts_command(args):
    """Generate charts for a test run"""
    try:
        bp_api = BreakingPointAPI(args.host, args.username, args.password)
        bp_api.login()
        
        # Ensure output directory exists
        os.makedirs(args.output_dir, exist_ok=True)
        
        chart_paths = generate_charts(
            bp_api, 
            args.test_id, 
            args.run_id, 
            args.output_dir
        )
        
        print(f"Generated {len(chart_paths)} charts:")
        for path in chart_paths:
            print(f"  - {path}")
        
        bp_api.logout()
        return 0
    except Exception as e:
        logger.error(f"Error generating charts: {str(e)}")
        return 1

def compare_test_results_command(args):
    """Compare two test runs"""
    try:
        bp_api = BreakingPointAPI(args.host, args.username, args.password)
        bp_api.login()
        
        comparison = compare_test_results(
            bp_api, 
            args.test_id1, 
            args.run_id1, 
            args.test_id2, 
            args.run_id2
        )
        
        test1_name = comparison.get("test1", {}).get("testName", "Test 1")
        test2_name = comparison.get("test2", {}).get("testName", "Test 2")
        print(f"Comparison of {test1_name} vs {test2_name}:")
        
        for metric_name, metric_data in comparison.get("metrics", {}).items():
            diff = metric_data.get("difference", {}).get("average", 0)
            pct = metric_data.get("difference", {}).get("percentage", 0)
            print(f"  {metric_name.capitalize()}: {diff} ({pct:.2f}%)")
        
        if args.chart_type:
            # Ensure output directory exists
            os.makedirs(args.output_dir, exist_ok=True)
            
            chart_path = compare_charts(
                bp_api, 
                args.test_id1, 
                args.run_id1, 
                args.test_id2, 
                args.run_id2, 
                args.chart_type, 
                args.output_dir
            )
            
            print(f"Comparison chart generated: {chart_path}")
        
        bp_api.logout()
        return 0
    except Exception as e:
        logger.error(f"Error comparing test results: {str(e)}")
        return 1

def main(args: Optional[List[str]] = None) -> int:
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Breaking Point MCP Agent CLI")
    
    # Global options
    parser.add_argument("--host", help="Breaking Point host")
    parser.add_argument("--username", help="Breaking Point username")
    parser.add_argument("--password", help="Breaking Point password")
    parser.add_argument("--config", help="Path to configuration file")
    parser.add_argument("--log-file", help="Path to log file")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    
    # Create subparsers for commands
    subparsers = parser.add_subparsers(title="commands", dest="command")
    
    # List tests command
    list_tests_parser = subparsers.add_parser("list-tests", help="List all available tests")
    list_tests_parser.set_defaults(func=list_tests_command)
    
    # Run test command
    run_test_parser = subparsers.add_parser("run-test", help="Run a test")
    run_test_parser.add_argument("test_id", help="Test ID")
    run_test_parser.set_defaults(func=run_test_command)
    
    # Generate report command
    report_parser = subparsers.add_parser("report", help="Generate a report for a test run")
    report_parser.add_argument("test_id", help="Test ID")
    report_parser.add_argument("run_id", help="Run ID")
    report_parser.add_argument("--type", choices=VALID_REPORT_TYPES, default="standard", help="Report type")
    report_parser.add_argument("--format", choices=VALID_OUTPUT_FORMATS, default="html", help="Output format")
    report_parser.add_argument("--output-dir", default=DEFAULT_REPORTS_DIR, help="Output directory")
    report_parser.set_defaults(func=generate_report_command)
    
    # Generate charts command
    charts_parser = subparsers.add_parser("charts", help="Generate charts for a test run")
    charts_parser.add_argument("test_id", help="Test ID")
    charts_parser.add_argument("run_id", help="Run ID")
    charts_parser.add_argument("--output-dir", default=DEFAULT_CHARTS_DIR, help="Output directory")
    charts_parser.set_defaults(func=generate_charts_command)
    
    # Compare test results command
    compare_parser = subparsers.add_parser("compare", help="Compare two test runs")
    compare_parser.add_argument("test_id1", help="First test ID")
    compare_parser.add_argument("run_id1", help="First run ID")
    compare_parser.add_argument("test_id2", help="Second test ID")
    compare_parser.add_argument("run_id2", help="Second run ID")
    compare_parser.add_argument("--chart-type", choices=VALID_CHART_TYPES, help="Generate comparison chart")
    compare_parser.add_argument("--output-dir", default=DEFAULT_CHARTS_DIR, help="Output directory for charts")
    compare_parser.set_defaults(func=compare_test_results_command)
    
    # Parse arguments
    parsed_args = parser.parse_args(args)
    
    # Configure logging
    log_level = logging.DEBUG if parsed_args.debug else logging.INFO
    configure_logging(level=log_level, log_file=parsed_args.log_file)
    
    # Load configuration if specified
    if parsed_args.config:
        try:
            config = load_config(parsed_args.config)
            
            # Apply configuration to arguments
            for key, value in config.items():
                if not getattr(parsed_args, key, None):
                    setattr(parsed_args, key, value)
        except Exception as e:
            logger.error(f"Error loading configuration: {str(e)}")
            return 1
    
    # Check if a command was provided
    if not hasattr(parsed_args, 'func'):
        parser.print_help()
        return 1
    
    # Check required arguments
    if not parsed_args.host:
        logger.error("Breaking Point host is required")
        return 1
    
    if not parsed_args.username:
        logger.error("Breaking Point username is required")
        return 1
        
    if not parsed_args.password:
        logger.error("Breaking Point password is required")
        return 1
    
    # Run the selected command
    return parsed_args.func(parsed_args)

if __name__ == "__main__":
    sys.exit(main())
