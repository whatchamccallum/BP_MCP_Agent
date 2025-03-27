#!/usr/bin/env python
"""
Getting Started with Breaking Point MCP Agent
Example script showing the basic workflow.
"""

import os
import sys
import time
import logging
from typing import Dict, Any, Optional

# Add the parent directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import from the BP MCP Agent package
from src.config import get_config
from src.init import initialize
from src.api import create_api
from src.analyzer import get_test_result_summary, generate_report, generate_charts

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
logger = logging.getLogger("GettingStarted")

def main():
    """Main function demonstrating the BP MCP Agent workflow"""
    # Step 1: Initialize the agent
    logger.info("Step 1: Initializing the BP MCP Agent")
    initialize()
    
    # Step 2: Configure API credentials
    logger.info("Step 2: Setting up API connection")
    
    # Get configuration from environment or config file
    config = get_config()
    
    # You can either use environment variables:
    # - BP_AGENT_API_HOST
    # - BP_AGENT_USERNAME
    # - BP_AGENT_PASSWORD
    
    # Or set credentials directly:
    if len(sys.argv) > 3:
        host = sys.argv[1]
        username = sys.argv[2]
        password = sys.argv[3]
    else:
        # Interactively prompt for credentials if not provided
        print("\nEnter Breaking Point connection details:")
        host = input("Breaking Point Host: ")
        username = input("Username: ")
        password = input("Password: ")
    
    # Step 3: Connect to Breaking Point
    logger.info("Step 3: Connecting to Breaking Point")
    api = create_api(host, username, password)
    
    try:
        with api:
            # Step 4: List available tests
            logger.info("Step 4: Listing available tests")
            tests = api.get_tests()
            
            print(f"\nFound {len(tests)} tests on Breaking Point system:")
            for i, test in enumerate(tests[:10]):  # Show only first 10 tests
                test_id = test.get("id", "Unknown")
                test_name = test.get("name", "Unknown")
                test_type = test.get("type", "Unknown")
                print(f"  {i+1}. {test_id}: {test_name} ({test_type})")
            
            if len(tests) > 10:
                print(f"  ... and {len(tests) - 10} more")
            
            # Step 5: Select a test to run (or use an existing test ID)
            logger.info("Step 5: Select and run a test")
            
            if len(tests) > 0:
                # Option to select a test from the list or enter a test ID
                selection = input("\nEnter test number to run or test ID (or press Enter to skip running a test): ")
                
                test_id = None
                if selection.isdigit() and 1 <= int(selection) <= len(tests):
                    # Selected by number
                    test_id = tests[int(selection) - 1].get("id")
                elif selection.strip():
                    # Entered test ID directly
                    test_id = selection.strip()
                
                if test_id:
                    # Run the selected test
                    print(f"Running test {test_id}...")
                    result = api.run_test(test_id)
                    run_id = result.get("runId")
                    
                    if run_id:
                        print(f"Test started with run ID: {run_id}")
                        
                        # Step 6: Wait for test completion
                        logger.info("Step 6: Waiting for test completion")
                        print("Waiting for test to complete...")
                        
                        max_wait = 300  # Maximum wait time in seconds
                        interval = 5  # Check interval in seconds
                        elapsed = 0
                        
                        while elapsed < max_wait:
                            status = api.get_test_status(test_id, run_id)
                            print(f"Test status: {status}")
                            
                            if status in ["completed", "stopped", "aborted", "failed"]:
                                break
                                
                            time.sleep(interval)
                            elapsed += interval
                        
                        if elapsed >= max_wait:
                            print(f"Test still running after {max_wait} seconds, proceeding anyway")
                        
                        # Step 7: Analyze test results
                        logger.info("Step 7: Analyzing test results")
                        print("Getting test results summary...")
                        
                        # Get and print summary
                        summary = get_test_result_summary(api, test_id, run_id)
                        
                        print(f"\nTest: {summary['testName']} ({summary['testType']})")
                        print(f"Status: {summary['status']}")
                        print(f"Duration: {summary['duration']} seconds")
                        
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
                        
                        # Step 8: Generate reports and charts
                        logger.info("Step 8: Generating reports and charts")
                        output_dir = "./getting_started_output"
                        os.makedirs(output_dir, exist_ok=True)
                        
                        # Generate report
                        report_path = generate_report(
                            api, test_id, run_id,
                            output_format="html",
                            report_type="standard",
                            output_dir=output_dir
                        )
                        print(f"Generated report: {report_path}")
                        
                        # Generate charts
                        chart_paths = generate_charts(api, test_id, run_id, output_dir=output_dir)
                        print(f"Generated {len(chart_paths)} charts:")
                        for path in chart_paths:
                            print(f"  {path}")
                            
                        print(f"\nAll output saved to {os.path.abspath(output_dir)}")
                    else:
                        print("Error: Failed to get run ID")
                
            else:
                print("No tests found. Try creating a test first.")
                    
            # Step 9: End of workflow
            logger.info("Workflow completed successfully")
            print("\nGetting started workflow completed!")
            print("Next steps:")
            print("  - Use the `main.py` script for CLI operations")
            print("  - Explore the API programmatically")
            print("  - Create custom analyzer plugins")
    
    except Exception as e:
        logger.error(f"Error in workflow: {e}")
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
