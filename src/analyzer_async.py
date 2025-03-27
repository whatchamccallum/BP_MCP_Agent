"""
Asynchronous Breaking Point Test Result Analyzer
This module provides asynchronous interfaces to the analyzer functionality for test results.
"""

import logging
import os
import asyncio
from typing import Dict, List, Optional, Union, Any, Tuple

from .analyzer.core import TestResultAnalyzer
from .api_async import AsyncBreakingPointAPI
from .exceptions import (
    APIError, 
    TestResultError, 
    ReportError, 
    ChartError,
    ValidationError
)

# Configure module logger
logger = logging.getLogger("BPAgent.AsyncAnalyzer")

def create_analyzer(bp_api: AsyncBreakingPointAPI) -> TestResultAnalyzer:
    """Create a test result analyzer
    
    Args:
        bp_api: Breaking Point API instance
        
    Returns:
        TestResultAnalyzer: Analyzer instance
    """
    return TestResultAnalyzer(bp_api)

async def get_test_result_summary(bp_api: AsyncBreakingPointAPI, test_id: str, run_id: str, use_cache: bool = True) -> Dict:
    """Asynchronously get a summary of test results
    
    Args:
        bp_api: Breaking Point API instance
        test_id: Test ID
        run_id: Run ID
        use_cache: Whether to use cached results if available
        
    Returns:
        Dict: Test result summary
        
    Raises:
        TestResultError: If there's an error retrieving or processing the test results
        APIError: If there's an API communication error
    """
    try:
        # Get the raw results first
        results = await bp_api.get_test_results(test_id, run_id, use_cache=use_cache)
        
        # Process the results to create a summary
        summary = {
            "testId": test_id,
            "runId": run_id,
            "testName": results.get("testName", "Unknown"),
            "testType": results.get("testType", "Unknown"),
            "startTime": results.get("startTime", "Unknown"),
            "endTime": results.get("endTime", "Unknown"),
            "duration": results.get("duration", 0),
            "status": results.get("status", "Unknown"),
            "metrics": {}
        }
        
        # Extract common metrics
        metrics = results.get("metrics", {})
        if "throughput" in metrics:
            summary["metrics"]["throughput"] = {
                "average": metrics["throughput"].get("average", 0),
                "maximum": metrics["throughput"].get("maximum", 0),
                "unit": "mbps"
            }
            
        # Cache the summary if caching is enabled
        if use_cache:
            from .cache import get_cache
            get_cache().set(test_id, run_id + "_summary", summary)
            
        if "latency" in metrics:
            summary["metrics"]["latency"] = {
                "average": metrics["latency"].get("average", 0),
                "maximum": metrics["latency"].get("maximum", 0),
                "unit": "ms"
            }
        
        # Test type-specific metrics
        if results.get("testType") == "strike":
            if "strikes" in metrics:
                summary["metrics"]["strikes"] = {
                    "attempted": metrics["strikes"].get("attempted", 0),
                    "blocked": metrics["strikes"].get("blocked", 0),
                    "allowed": metrics["strikes"].get("allowed", 0),
                    "successRate": metrics["strikes"].get("successRate", 0)
                }
                
        elif results.get("testType") in ["appsim", "clientsim"]:
            if "transactions" in metrics:
                summary["metrics"]["transactions"] = {
                    "attempted": metrics["transactions"].get("attempted", 0),
                    "successful": metrics["transactions"].get("successful", 0),
                    "failed": metrics["transactions"].get("failed", 0),
                    "successRate": metrics["transactions"].get("successRate", 0)
                }
        
        return summary
        
    except APIError:
        # Re-raise API errors directly
        raise
    except Exception as e:
        logger.error(f"Error getting test result summary for test {test_id}, run {run_id}: {str(e)}")
        raise TestResultError(f"Failed to get test result summary: {str(e)}") from e

async def compare_test_results(bp_api: AsyncBreakingPointAPI, 
                         test_id1: str, run_id1: str, 
                         test_id2: str, run_id2: str,
                         use_cache: bool = True) -> Dict:
    """Asynchronously compare two test results
    
    Args:
        bp_api: Breaking Point API instance
        test_id1: First test ID
        run_id1: First run ID
        test_id2: Second test ID
        run_id2: Second run ID
        use_cache: Whether to use cached results if available
        
    Returns:
        Dict: Comparison results
        
    Raises:
        TestResultError: If there's an error comparing the test results
        APIError: If there's an API communication error
    """
    try:
        # Get summaries for both tests concurrently
        summary_tasks = [
            get_test_result_summary(bp_api, test_id1, run_id1, use_cache=use_cache),
            get_test_result_summary(bp_api, test_id2, run_id2, use_cache=use_cache)
        ]
        
        summaries = await asyncio.gather(*summary_tasks)
        result1, result2 = summaries
        
        # Compare the results
        comparison = {
            "test1": {
                "testId": result1.get("testId", "Unknown"),
                "runId": result1.get("runId", "Unknown"),
                "testName": result1.get("testName", "Unknown")
            },
            "test2": {
                "testId": result2.get("testId", "Unknown"),
                "runId": result2.get("runId", "Unknown"),
                "testName": result2.get("testName", "Unknown")
            },
            "metrics": {}
        }
        
        # Compare common metrics
        for metric in ["throughput", "latency"]:
            if metric in result1.get("metrics", {}) and metric in result2.get("metrics", {}):
                metric1_avg = result1["metrics"][metric].get("average", 0)
                metric2_avg = result2["metrics"][metric].get("average", 0)
                
                # Calculate difference and percentage safely
                diff = metric2_avg - metric1_avg
                percentage = 0
                if metric1_avg > 0:
                    percentage = (diff / metric1_avg) * 100
                
                comparison["metrics"][metric] = {
                    "test1": result1["metrics"][metric],
                    "test2": result2["metrics"][metric],
                    "difference": {
                        "average": diff,
                        "percentage": percentage
                    }
                }
                
        # Compare test type-specific metrics
        if "strikes" in result1.get("metrics", {}) and "strikes" in result2.get("metrics", {}):
            comparison["metrics"]["strikes"] = {
                "test1": result1["metrics"]["strikes"],
                "test2": result2["metrics"]["strikes"],
                "difference": {
                    "successRate": result2["metrics"]["strikes"]["successRate"] - result1["metrics"]["strikes"]["successRate"]
                }
            }
            
        if "transactions" in result1.get("metrics", {}) and "transactions" in result2.get("metrics", {}):
            comparison["metrics"]["transactions"] = {
                "test1": result1["metrics"]["transactions"],
                "test2": result2["metrics"]["transactions"],
                "difference": {
                    "successRate": result2["metrics"]["transactions"]["successRate"] - result1["metrics"]["transactions"]["successRate"]
                }
            }
            
        return comparison
        
    except APIError:
        # Re-raise API errors directly
        raise
    except Exception as e:
        logger.error(f"Error comparing test results: {str(e)}")
        raise TestResultError(f"Failed to compare test results: {str(e)}") from e

async def batch_process_tests(bp_api: AsyncBreakingPointAPI, test_runs: List[Tuple[str, str]], 
                       output_dir: str = "./", report_type: str = "standard",
                       use_cache: bool = True) -> List[Dict]:
    """Process a batch of test runs concurrently
    
    Args:
        bp_api: Breaking Point API instance
        test_runs: List of (test_id, run_id) tuples
        output_dir: Output directory for reports and charts
        report_type: Report type (standard, executive, detailed, compliance)
        use_cache: Whether to use cached results if available
        
    Returns:
        List[Dict]: List of test result summaries
        
    Raises:
        ValidationError: If the report type is invalid
        APIError: If there's an API communication error
    """
    # Validate report type
    valid_types = ["standard", "executive", "detailed", "compliance"]
    if report_type not in valid_types:
        raise ValidationError(f"Invalid report type: {report_type}. "
                            f"Must be one of: {', '.join(valid_types)}")
    
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Create tasks for getting summaries
    summary_tasks = [
        get_test_result_summary(bp_api, test_id, run_id, use_cache=use_cache)
        for test_id, run_id in test_runs
    ]
    
    # Execute all tasks concurrently
    summaries = await asyncio.gather(*summary_tasks, return_exceptions=True)
    
    # Process results
    results = []
    errors = []
    
    for i, (test_id, run_id) in enumerate(test_runs):
        summary = summaries[i]
        
        if isinstance(summary, Exception):
            logger.error(f"Error processing test {test_id}, run {run_id}: {summary}")
            errors.append((test_id, run_id, str(summary)))
        else:
            results.append(summary)
    
    # Log summary of processing
    if errors:
        logger.warning(f"Completed batch processing with {len(errors)} errors out of {len(test_runs)} tests")
        for test_id, run_id, error in errors:
            logger.warning(f"  Test {test_id}, run {run_id}: {error}")
    else:
        logger.info(f"Successfully processed all {len(test_runs)} tests")
            
    return results

async def get_multiple_test_statuses(bp_api: AsyncBreakingPointAPI, test_runs: List[Tuple[str, str]]) -> Dict[str, str]:
    """Get the status of multiple test runs concurrently
    
    Args:
        bp_api: Breaking Point API instance
        test_runs: List of (test_id, run_id) tuples
        
    Returns:
        Dict[str, str]: Dictionary mapping test IDs to their status
    """
    # Create tasks for getting statuses
    status_tasks = [
        bp_api.get_test_status(test_id, run_id)
        for test_id, run_id in test_runs
    ]
    
    # Execute all tasks concurrently
    statuses = await asyncio.gather(*status_tasks, return_exceptions=True)
    
    # Process results
    result = {}
    for i, (test_id, run_id) in enumerate(test_runs):
        status = statuses[i]
        
        if isinstance(status, Exception):
            logger.error(f"Error getting status for test {test_id}, run {run_id}: {status}")
            result[test_id] = "error"
        else:
            result[test_id] = status
            
    return result

async def run_and_analyze_tests(bp_api: AsyncBreakingPointAPI, test_ids: List[str], 
                              wait_for_completion: bool = True,
                              poll_interval: int = 10,
                              timeout: int = 3600) -> Dict[str, Dict]:
    """Run tests, wait for completion, and analyze results in a single operation
    
    Args:
        bp_api: Breaking Point API instance
        test_ids: List of test IDs to run
        wait_for_completion: Whether to wait for tests to complete
        poll_interval: Polling interval in seconds when waiting
        timeout: Maximum time to wait in seconds
        
    Returns:
        Dict[str, Dict]: Dictionary mapping test IDs to their results/status
    """
    # Run all tests concurrently
    run_ids = await bp_api.run_multiple_tests(test_ids)
    
    # If not waiting for completion, return the run IDs
    if not wait_for_completion:
        return {test_id: {"status": "running", "runId": run_id} for test_id, run_id in run_ids.items()}
    
    # Wait for all tests to complete with timeout
    test_runs = run_ids
    start_time = asyncio.get_event_loop().time()
    
    while True:
        # Get status for all tests
        statuses = await bp_api.wait_for_tests_completion(test_runs, poll_interval=poll_interval)
        
        # Check if all tests have completed
        all_completed = all(status in ["completed", "stopped", "error", "failed"] 
                           for status in statuses.values())
        
        if all_completed:
            break
            
        # Check for timeout
        elapsed = asyncio.get_event_loop().time() - start_time
        if elapsed > timeout:
            logger.warning(f"Timeout waiting for tests to complete after {elapsed:.1f} seconds")
            break
    
    # Get results for all completed tests
    results = {}
    for test_id, run_id in test_runs.items():
        if run_id is not None:
            try:
                # Get summary for each test
                summary = await get_test_result_summary(bp_api, test_id, run_id)
                results[test_id] = summary
            except Exception as e:
                logger.error(f"Error getting results for test {test_id}: {e}")
                results[test_id] = {"status": "error", "error": str(e)}
        else:
            results[test_id] = {"status": "error", "error": "Failed to start test"}
            
    return results
