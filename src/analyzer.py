"""
Breaking Point Test Result Analyzer
This module provides a clean interface to the analyzer functionality for test results.
It delegates to the modular analyzer components for implementation.
"""

import logging
import os
from typing import Dict, List, Optional, Union, Any, Tuple

from .analyzer.core import TestResultAnalyzer
from .analyzer.plugins.registry import discover_plugins, get_plugin_manager
from .analyzer.plugins.base import TestSummary
from .api import BreakingPointAPI
from .exceptions import (
    APIError, 
    TestResultError, 
    ReportError, 
    ChartError,
    ValidationError
)

# Configure module logger
logger = logging.getLogger("BPAgent.Analyzer")

def initialize_plugins(plugin_dirs: Optional[List[str]] = None) -> None:
    """Initialize and load plugins from specified directories
    
    Args:
        plugin_dirs: List of directories to search for plugins (default: None)
    """
    discover_plugins(plugin_dirs)

def create_analyzer(bp_api: BreakingPointAPI) -> TestResultAnalyzer:
    """Create a test result analyzer
    
    Args:
        bp_api: Breaking Point API instance
        
    Returns:
        TestResultAnalyzer: Analyzer instance
    """
    return TestResultAnalyzer(bp_api)

def get_test_result_summary(bp_api: BreakingPointAPI, test_id: str, run_id: str, use_cache: bool = True) -> TestSummary:
    """Get a summary of test results
    
    Args:
        bp_api: Breaking Point API instance
        test_id: Test ID
        run_id: Run ID
        use_cache: Whether to use cached results if available
        
    Returns:
        TestSummary: Test result summary
        
    Raises:
        TestResultError: If there's an error retrieving or processing the test results
        APIError: If there's an API communication error
    """
    try:
        analyzer = create_analyzer(bp_api)
        return analyzer.get_test_result_summary(test_id, run_id, use_cache=use_cache)
    except APIError:
        # Re-raise API errors directly
        raise
    except Exception as e:
        logger.error(f"Error getting test result summary for test {test_id}, run {run_id}: {str(e)}")
        raise TestResultError(f"Failed to get test result summary: {str(e)}") from e

def compare_test_results(bp_api: BreakingPointAPI, 
                         test_id1: str, run_id1: str, 
                         test_id2: str, run_id2: str,
                         use_cache: bool = True) -> Dict[str, Any]:
    """Compare two test results
    
    Args:
        bp_api: Breaking Point API instance
        test_id1: First test ID
        run_id1: First run ID
        test_id2: Second test ID
        run_id2: Second run ID
        use_cache: Whether to use cached results if available
        
    Returns:
        Dict[str, Any]: Comparison results
        
    Raises:
        TestResultError: If there's an error comparing the test results
        APIError: If there's an API communication error
    """
    try:
        analyzer = create_analyzer(bp_api)
        result1 = analyzer.get_test_result_summary(test_id1, run_id1, use_cache=use_cache)
        result2 = analyzer.get_test_result_summary(test_id2, run_id2, use_cache=use_cache)
        return analyzer.compare_test_results(result1, result2)
    except APIError:
        # Re-raise API errors directly
        raise
    except Exception as e:
        logger.error(f"Error comparing test results: {str(e)}")
        raise TestResultError(f"Failed to compare test results: {str(e)}") from e

def generate_report(bp_api: BreakingPointAPI, test_id: str, run_id: str, 
                   output_format: str = "html", report_type: str = "standard", 
                   output_dir: str = "./") -> str:
    """Generate a report for a test run
    
    Args:
        bp_api: Breaking Point API instance
        test_id: Test ID
        run_id: Run ID
        output_format: Output format (html, pdf, csv)
        report_type: Report type (standard, executive, detailed, compliance)
        output_dir: Directory to save the report in
        
    Returns:
        str: Path to the generated report file
        
    Raises:
        ReportError: If there's an error generating the report
        ValidationError: If the report type or output format is invalid
        APIError: If there's an API communication error
    """
    # Validate input parameters
    valid_formats = ["html", "csv", "pdf", "txt"]
    
    if output_format not in valid_formats:
        raise ValidationError(f"Invalid output format: {output_format}. "
                            f"Must be one of: {', '.join(valid_formats)}")
    
    # Check if the report generator exists
    plugin_manager = get_plugin_manager()
    if report_type not in plugin_manager.report_generators:
        valid_types = list(plugin_manager.report_generators.keys())
        raise ValidationError(f"Invalid report type: {report_type}. "
                            f"Must be one of: {', '.join(valid_types)}")
    
    try:
        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)
        
        analyzer = create_analyzer(bp_api)
        return analyzer.generate_report(test_id, run_id, output_format, report_type, output_dir)
    except APIError:
        # Re-raise API errors directly
        raise
    except ValidationError:
        # Re-raise validation errors directly
        raise
    except Exception as e:
        logger.error(f"Error generating report for test {test_id}, run {run_id}: {str(e)}")
        raise ReportError(f"Failed to generate report: {str(e)}") from e

def generate_report_from_summary(bp_api: BreakingPointAPI, summary: TestSummary, 
                                output_format: str = "html", report_type: str = "standard",
                                output_dir: str = "./") -> str:
    """Generate a report from an existing test result summary
    
    Args:
        bp_api: Breaking Point API instance
        summary: Test result summary dictionary
        output_format: Output format (html, pdf, csv)
        report_type: Report type (standard, executive, detailed, compliance)
        output_dir: Directory to save the report in
        
    Returns:
        str: Path to the generated report file
        
    Raises:
        ReportError: If there's an error generating the report
        ValidationError: If the report type, output format, or summary is invalid
        APIError: If there's an API communication error
    """
    # Validate input parameters
    valid_formats = ["html", "csv", "pdf", "txt"]
    
    if output_format not in valid_formats:
        raise ValidationError(f"Invalid output format: {output_format}. "
                            f"Must be one of: {', '.join(valid_formats)}")
    
    # Check if the report generator exists
    plugin_manager = get_plugin_manager()
    if report_type not in plugin_manager.report_generators:
        valid_types = list(plugin_manager.report_generators.keys())
        raise ValidationError(f"Invalid report type: {report_type}. "
                            f"Must be one of: {', '.join(valid_types)}")
    
    # Validate summary has required fields
    required_fields = ["testName", "testType", "startTime", "endTime", "duration", "status", "metrics"]
    missing_fields = [field for field in required_fields if field not in summary]
    if missing_fields:
        raise ValidationError(f"Summary missing required fields: {', '.join(missing_fields)}")
    
    try:
        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)
        
        analyzer = create_analyzer(bp_api)
        return analyzer.generate_report_from_summary(summary, output_format, report_type, output_dir)
    except APIError:
        # Re-raise API errors directly
        raise
    except ValidationError:
        # Re-raise validation errors directly
        raise
    except Exception as e:
        logger.error(f"Error generating report from summary for test {summary.get('testName', 'Unknown')}: {str(e)}")
        raise ReportError(f"Failed to generate report from summary: {str(e)}") from e

def generate_charts(bp_api: BreakingPointAPI, test_id: str, run_id: str, 
                   output_dir: str = "./") -> List[str]:
    """Generate charts for test results
    
    Args:
        bp_api: Breaking Point API instance
        test_id: Test ID
        run_id: Run ID
        output_dir: Output directory
        
    Returns:
        List[str]: Paths to generated chart files
        
    Raises:
        ChartError: If there's an error generating the charts
        APIError: If there's an API communication error
    """
    try:
        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)
        
        analyzer = create_analyzer(bp_api)
        return analyzer.generate_charts(test_id, run_id, output_dir)
    except APIError:
        # Re-raise API errors directly
        raise
    except Exception as e:
        logger.error(f"Error generating charts for test {test_id}, run {run_id}: {str(e)}")
        raise ChartError(f"Failed to generate charts: {str(e)}") from e

def compare_charts(bp_api: BreakingPointAPI, 
                  test_id1: str, run_id1: str, 
                  test_id2: str, run_id2: str, 
                  chart_type: str, 
                  output_dir: str = "./") -> str:
    """Generate a comparison chart for two test runs
    
    Args:
        bp_api: Breaking Point API instance
        test_id1: First test ID
        run_id1: First run ID
        test_id2: Second test ID
        run_id2: Second run ID
        chart_type: Chart type (throughput, latency, strikes, transactions)
        output_dir: Output directory
        
    Returns:
        str: Path to the generated chart file
        
    Raises:
        ChartError: If there's an error generating the comparison chart
        ValidationError: If the chart type is invalid
        APIError: If there's an API communication error
    """
    # Validate chart type
    valid_chart_types = ["throughput", "latency", "strikes", "transactions"]
    if chart_type not in valid_chart_types:
        raise ValidationError(f"Invalid chart type: {chart_type}. "
                            f"Must be one of: {', '.join(valid_chart_types)}")
    
    try:
        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)
        
        analyzer = create_analyzer(bp_api)
        chart_path = analyzer.compare_charts(test_id1, run_id1, test_id2, run_id2, chart_type, output_dir)
        
        # Validate the chart was actually created
        if not chart_path or not os.path.exists(chart_path):
            raise ChartError(f"Failed to generate comparison chart for {chart_type}")
            
        return chart_path
    except APIError:
        # Re-raise API errors directly
        raise
    except ValidationError:
        # Re-raise validation errors directly
        raise
    except Exception as e:
        logger.error(f"Error generating comparison chart: {str(e)}")
        raise ChartError(f"Failed to generate comparison chart: {str(e)}") from e

def get_raw_test_results(bp_api: BreakingPointAPI, test_id: str, run_id: str) -> Dict[str, Any]:
    """Get raw test results directly from the API
    
    Args:
        bp_api: Breaking Point API instance
        test_id: Test ID
        run_id: Run ID
        
    Returns:
        Dict[str, Any]: Raw test results
        
    Raises:
        APIError: If there's an API communication error
    """
    return bp_api.get_test_results(test_id, run_id)

def batch_process_tests(bp_api: BreakingPointAPI, test_runs: List[Tuple[str, str]], 
                       output_dir: str = "./", report_type: str = "standard",
                       use_cache: bool = True) -> List[TestSummary]:
    """Process a batch of test runs
    
    Args:
        bp_api: Breaking Point API instance
        test_runs: List of (test_id, run_id) tuples
        output_dir: Output directory for reports and charts
        report_type: Report type (standard, executive, detailed, compliance)
        use_cache: Whether to use cached results if available
        
    Returns:
        List[TestSummary]: List of test result summaries
        
    Raises:
        ValidationError: If the report type is invalid
        APIError: If there's an API communication error
    """
    # Check if the report generator exists
    plugin_manager = get_plugin_manager()
    if report_type not in plugin_manager.report_generators:
        valid_types = list(plugin_manager.report_generators.keys())
        raise ValidationError(f"Invalid report type: {report_type}. "
                            f"Must be one of: {', '.join(valid_types)}")
    
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    analyzer = create_analyzer(bp_api)
    results: List[TestSummary] = []
    errors = []
    
    for test_id, run_id in test_runs:
        try:
            # Get summary
            logger.info(f"Processing test {test_id}, run {run_id}")
            summary = analyzer.get_test_result_summary(test_id, run_id, use_cache=use_cache)
            results.append(summary)
            
            # Generate report
            report_path = analyzer.generate_report(test_id, run_id, "html", report_type, output_dir)
            logger.info(f"Generated report: {report_path}")
            
            # Generate charts
            chart_paths = analyzer.generate_charts(test_id, run_id, output_dir)
            logger.info(f"Generated {len(chart_paths)} charts")
            
        except Exception as e:
            logger.error(f"Error processing test {test_id}, run {run_id}: {e}")
            errors.append((test_id, run_id, str(e)))
    
    # Log summary of processing
    if errors:
        logger.warning(f"Completed batch processing with {len(errors)} errors out of {len(test_runs)} tests")
        for test_id, run_id, error in errors:
            logger.warning(f"  Test {test_id}, run {run_id}: {error}")
    else:
        logger.info(f"Successfully processed all {len(test_runs)} tests")
            
    return results
