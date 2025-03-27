#!/usr/bin/env python
"""
Validation Script for Breaking Point Analyzer
This script helps validate that the analyzer module works correctly.
It tests the basic functionality of the analyzer module against a live Breaking Point instance.
"""

import sys
import os
import logging
import argparse
from datetime import datetime
import traceback
from typing import List, Tuple

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from src.api import BreakingPointAPI
from src.analyzer import (
    get_test_result_summary,
    compare_test_results,
    generate_report,
    generate_charts,
    compare_charts,
    batch_process_tests
)
from src.utils import configure_logging
from src.exceptions import APIError, TestResultError, ReportError, ChartError, ValidationError

def validate_analyzer(host: str, username: str, password: str, test_id: str, run_id: str, 
                     output_dir: str, second_test_id: str = None, second_run_id: str = None,
                     use_cache: bool = True, clear_cache: bool = False) -> bool:
    """
    Validate the analyzer module with a real Breaking Point test.
    
    Args:
        host: Breaking Point host
        username: Breaking Point username
        password: Breaking Point password
        test_id: Test ID to use for validation
        run_id: Run ID to use for validation
        output_dir: Output directory for reports and charts
        second_test_id: Optional second test ID for comparison
        second_run_id: Optional second run ID for comparison
        
    Returns:
        bool: True if validation successful, False otherwise
    """
    bp_api = None
    success = True
    errors = []
    
    try:
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        # Clear the cache if requested
        if clear_cache:
            from src.cache import get_cache
            count = get_cache().clear()
            logger.info(f"Cleared {count} cache entries")
        
        # Create API instance
        logger.info("Creating Breaking Point API instance...")
        bp_api = BreakingPointAPI(host, username, password)
        
        # Login
        logger.info("Logging in to Breaking Point...")
        bp_api.login()
        logger.info("Login successful")
            
        # Test get_test_result_summary
        logger.info(f"Getting test result summary for test {test_id}, run {run_id}...")
        summary = get_test_result_summary(bp_api, test_id, run_id, use_cache=use_cache)
        logger.info(f"Test name: {summary.get('testName', 'Unknown')}")
        logger.info(f"Test status: {summary.get('status', 'Unknown')}")
        
        # Test generate_report
        logger.info("Generating a standard HTML report...")
        report_path = generate_report(bp_api, test_id, run_id, "html", "standard", output_dir)
        logger.info(f"Report generated: {report_path}")
        
        # Test generate_charts
        logger.info("Generating charts...")
        chart_paths = generate_charts(bp_api, test_id, run_id, output_dir)
        logger.info(f"Generated {len(chart_paths)} charts")
        
        # If a second test/run is available, test comparison functions
        if second_test_id and second_run_id:
            logger.info(f"Comparing test {test_id} with test {second_test_id}...")
            comparison = compare_test_results(bp_api, test_id, run_id, second_test_id, second_run_id)
            logger.info("Comparison successful")
            
            # Test chart types
            for chart_type in ["throughput", "latency"]:
                try:
                    logger.info(f"Generating {chart_type} comparison chart...")
                    chart_path = compare_charts(bp_api, test_id, run_id, second_test_id, second_run_id, chart_type, output_dir)
                    logger.info(f"Comparison chart generated: {chart_path}")
                except Exception as e:
                    logger.warning(f"Failed to generate {chart_type} comparison chart: {str(e)}")
                    errors.append(f"Comparison chart ({chart_type}): {str(e)}")
                    success = False
            
            # Test batch processing
            logger.info("Testing batch processing...")
            test_runs = [(test_id, run_id), (second_test_id, second_run_id)]
            results = batch_process_tests(bp_api, test_runs, os.path.join(output_dir, "batch"), "standard")
            logger.info(f"Processed {len(results)} test runs")
            
    except APIError as e:
        logger.error(f"API Error: {str(e)}")
        if hasattr(e, 'status_code'):
            logger.error(f"Status Code: {e.status_code}")
        errors.append(f"API Error: {str(e)}")
        success = False
    except TestResultError as e:
        logger.error(f"Test Result Error: {str(e)}")
        errors.append(f"Test Result Error: {str(e)}")
        success = False
    except ReportError as e:
        logger.error(f"Report Error: {str(e)}")
        errors.append(f"Report Error: {str(e)}")
        success = False
    except ChartError as e:
        logger.error(f"Chart Error: {str(e)}")
        errors.append(f"Chart Error: {str(e)}")
        success = False
    except ValidationError as e:
        logger.error(f"Validation Error: {str(e)}")
        errors.append(f"Validation Error: {str(e)}")
        success = False
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        logger.error(traceback.format_exc())
        errors.append(f"Unexpected error: {str(e)}")
        success = False
    finally:
        # Logout
        if bp_api and bp_api.auth_token:
            logger.info("Logging out from Breaking Point...")
            bp_api.logout()
    
    # Print summary
    if success:
        logger.info("Validation completed successfully!")
    else:
        logger.error("Validation failed with the following errors:")
        for error in errors:
            logger.error(f"  - {error}")
    
    return success

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Validate the Breaking Point Analyzer")
    parser.add_argument("host", help="Breaking Point host address")
    parser.add_argument("username", help="Breaking Point username")
    parser.add_argument("password", help="Breaking Point password")
    parser.add_argument("test_id", help="Test ID to use for validation")
    parser.add_argument("run_id", help="Run ID to use for validation")
    parser.add_argument("--second-test-id", help="Second test ID for comparison (optional)")
    parser.add_argument("--second-run-id", help="Second run ID for comparison (optional)")
    parser.add_argument("--output-dir", default="./validation_output", help="Output directory")
    parser.add_argument("--log-file", default="validation.log", help="Log file path")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    
    # Cache options
    parser.add_argument("--use-cache", action="store_true", default=True,
                      help="Use cached results when available")
    parser.add_argument("--no-cache", action="store_true", default=False,
                      help="Disable result caching")
    parser.add_argument("--clear-cache", action="store_true", default=False,
                      help="Clear the cache before running")
    
    args = parser.parse_args()
    
    # Configure logging
    log_dir = os.path.dirname(args.log_file)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir, exist_ok=True)
        
    configure_logging(
        level=logging.DEBUG if args.debug else logging.INFO,
        log_file=args.log_file
    )
    
    # Create timestamp-based output directory
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = os.path.join(args.output_dir, f"validation_{timestamp}")
    
    # Determine if caching should be used
    use_cache = args.use_cache and not args.no_cache
    
    # Run validation
    success = validate_analyzer(
        args.host,
        args.username,
        args.password,
        args.test_id,
        args.run_id,
        output_dir,
        args.second_test_id,
        args.second_run_id,
        use_cache,
        args.clear_cache
    )
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    logger = logging.getLogger("Validation")
    main()
