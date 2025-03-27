#!/usr/bin/env python
"""
Example of using the asynchronous API and analyzer
This script demonstrates how to use the async capabilities for improved performance.
"""

import os
import asyncio
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
logger = logging.getLogger("AsyncExample")

# Add the parent directory to sys.path for imports
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.api_async import AsyncBreakingPointAPI
from src.analyzer_async import get_test_result_summary, batch_process_tests, run_and_analyze_tests

async def example_concurrent_test_runs(api, test_ids):
    """Example of running multiple tests concurrently"""
    logger.info(f"Running {len(test_ids)} tests concurrently")
    
    # Start all tests concurrently
    run_ids = await api.run_multiple_tests(test_ids)
    logger.info(f"Tests started with run IDs: {run_ids}")
    
    # Wait for all tests to complete
    statuses = await api.wait_for_tests_completion(run_ids)
    logger.info(f"Tests completed with statuses: {statuses}")
    
    # Get results for all tests
    results = await api.get_multiple_test_results(run_ids)
    
    return results

async def example_concurrent_analysis(api, test_runs):
    """Example of analyzing multiple test results concurrently"""
    logger.info(f"Analyzing {len(test_runs)} test results concurrently")
    
    # Process all tests concurrently and save reports to the output directory
    output_dir = "./results"
    os.makedirs(output_dir, exist_ok=True)
    
    # Process all test results
    start_time = datetime.now()
    summaries = await batch_process_tests(api, test_runs, output_dir=output_dir)
    elapsed = (datetime.now() - start_time).total_seconds()
    
    logger.info(f"Processed {len(summaries)} test results in {elapsed:.2f} seconds")
    return summaries

async def example_run_and_analyze(api, test_ids):
    """Example of running tests and analyzing results in a single operation"""
    logger.info(f"Running and analyzing {len(test_ids)} tests")
    
    # Run tests and get results
    results = await run_and_analyze_tests(api, test_ids)
    
    logger.info(f"Completed run and analysis for {len(results)} tests")
    return results

async def main():
    """Main example function"""
    # BP system connection details (replace with actual values)
    host = "bp-system.example.com"
    username = "admin"
    password = "password"
    
    # Example test IDs (replace with actual test IDs)
    test_ids = ["test1", "test2", "test3"]
    test_runs = [("test1", "run1"), ("test2", "run2"), ("test3", "run3")]
    
    # Create async API instance
    async with AsyncBreakingPointAPI(host, username, password) as api:
        # Uncomment the example you want to run
        
        # Example 1: Run multiple tests concurrently
        # results = await example_concurrent_test_runs(api, test_ids)
        
        # Example 2: Analyze multiple test results concurrently
        # summaries = await example_concurrent_analysis(api, test_runs)
        
        # Example 3: Run and analyze tests in a single operation
        # results = await example_run_and_analyze(api, test_ids)
        
        # Just list tests as a simple example
        logger.info("Listing available tests...")
        tests = await api.get_tests()
        logger.info(f"Found {len(tests)} tests")
        
if __name__ == "__main__":
    # Run the async main function
    asyncio.run(main())
