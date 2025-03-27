"""
Test Result Analyzer Core
This module provides the main TestResultAnalyzer class, now using a plugin architecture.
"""

import logging
import os
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Union, Any, TextIO, cast

from ..api import BreakingPointAPI
from .plugins.base import TestSummary
from .plugins.registry import (
    get_plugin_manager,
    get_report_generator,
    get_chart_generator
)

logger = logging.getLogger("BPAgent.Analyzer")

class TestResultAnalyzer:
    """Analyzes test results and generates reports using a plugin architecture"""
    
    def __init__(self, bp_api: BreakingPointAPI):
        """Initialize the test result analyzer
        
        Args:
            bp_api: Breaking Point API instance
        """
        self.bp_api = bp_api
        
    def get_test_result_summary(self, test_id: str, run_id: str, use_cache: bool = True) -> TestSummary:
        """Get a summary of test results
        
        Args:
            test_id: Test ID
            run_id: Run ID
            use_cache: Whether to use cached results
            
        Returns:
            TestSummary: Test result summary
        """
        # Try to get the summary from cache first
        if use_cache:
            from ..cache import get_cache
            cache_key = f"summary_{test_id}_{run_id}"
            cached_summary = get_cache().get(test_id, run_id + "_summary")
            if cached_summary:
                logger.debug(f"Using cached summary for test {test_id}, run {run_id}")
                return cast(TestSummary, cached_summary)
    
        # Get the detailed results (which might come from cache)
        results = self.bp_api.get_test_results(test_id, run_id, use_cache=use_cache)
        
        # Extract summary metrics
        summary: TestSummary = {
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
            from ..cache import get_cache
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
        
    def compare_test_results(self, result1: TestSummary, result2: TestSummary) -> Dict[str, Any]:
        """Compare two test results
        
        Args:
            result1: First test result
            result2: Second test result
            
        Returns:
            Dict: Comparison results
        """
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

    def _create_output_filename(self, test_id: str, run_id: str, report_type: str, 
                              output_format: str, output_dir: str) -> str:
        """Create a standardized output filename
        
        Args:
            test_id: Test ID
            run_id: Run ID
            report_type: Report type
            output_format: Output format
            output_dir: Output directory
            
        Returns:
            str: Full path to the output file
        """
        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)
        
        # Create filename
        filename = f"report_{test_id}_{run_id}_{report_type}.{output_format}"
        return os.path.join(output_dir, filename)

    def generate_report(self, test_id: str, run_id: str, output_format: str = "html", 
                       report_type: str = "standard", output_dir: str = "./") -> str:
        """Generate a report for a test run using the appropriate plugin
        
        Args:
            test_id: Test ID
            run_id: Run ID
            output_format: Output format (html, pdf, csv)
            report_type: Report type (standard, executive, detailed, compliance)
            output_dir: Directory to save the report in
            
        Returns:
            str: Path to the generated report file
            
        Raises:
            ValueError: If the report type is not supported
        """
        # Get the test result summary
        summary = self.get_test_result_summary(test_id, run_id)
        
        # Generate report from summary
        return self.generate_report_from_summary(summary, output_format, report_type, output_dir)
    
    def generate_report_from_summary(self, summary: TestSummary, output_format: str = "html",
                                    report_type: str = "standard", output_dir: str = "./") -> str:
        """Generate a report from an existing test result summary using the appropriate plugin
        
        Args:
            summary: Test result summary
            output_format: Output format (html, pdf, csv)
            report_type: Report type (standard, executive, detailed, compliance)
            output_dir: Directory to save the report in
            
        Returns:
            str: Path to the generated report file
            
        Raises:
            ValueError: If the report type is not supported
        """
        # Create the output filename
        test_id = summary.get("testId", "unknown")
        run_id = summary.get("runId", "unknown")
        filename = self._create_output_filename(test_id, run_id, report_type, output_format, output_dir)
        
        # Try to get additional raw data if detailed report is requested
        raw_results = {}
        if report_type in ["detailed", "compliance"]:
            try:
                raw_results = self.bp_api.get_test_results(test_id, run_id)
            except Exception as e:
                logger.warning(f"Could not retrieve detailed results: {e}")
        
        # Get the appropriate report generator plugin
        generator = get_report_generator(report_type)
        if not generator:
            raise ValueError(f"Unsupported report type: {report_type}")
        
        # Generate the report
        try:
            return generator.generate(summary, raw_results, output_format, filename)
        except Exception as e:
            logger.error(f"Error generating report: {e}")
            raise
            
    def generate_charts(self, test_id: str, run_id: str, output_dir: str = "./") -> List[str]:
        """Generate charts for test results using the appropriate plugins
        
        Args:
            test_id: Test ID
            run_id: Run ID
            output_dir: Output directory
            
        Returns:
            List[str]: Paths to generated chart files
        """
        # Get the test result summary
        summary = self.get_test_result_summary(test_id, run_id)
        
        # Try to get additional raw data for more detailed charts
        try:
            raw_results = self.bp_api.get_test_results(test_id, run_id)
        except Exception as e:
            logger.warning(f"Could not retrieve detailed results: {e}")
            raw_results = {}
        
        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)
        
        chart_files = []
        
        # Determine which charts to generate based on test type and metrics
        generators = {
            "throughput": "throughput" in summary.get("metrics", {}),
            "latency": "latency" in summary.get("metrics", {}),
            "strikes": "strikes" in summary.get("metrics", {}),
            "transactions": "transactions" in summary.get("metrics", {})
        }
        
        # Generate each applicable chart
        for chart_type, should_generate in generators.items():
            if should_generate:
                try:
                    generator = get_chart_generator(chart_type)
                    if generator:
                        # Create filename
                        filename = os.path.join(output_dir, f"chart_{test_id}_{run_id}_{chart_type}.png")
                        # Generate chart
                        chart_file = generator.generate(summary, raw_results, filename)
                        chart_files.append(chart_file)
                except Exception as e:
                    logger.error(f"Error generating {chart_type} chart: {e}")
        
        return chart_files
    
    def compare_charts(self, test_id1: str, run_id1: str, test_id2: str, run_id2: str, 
                      chart_type: str, output_dir: str = "./") -> str:
        """Generate a comparison chart for two test runs using the comparison plugin
        
        Args:
            test_id1: First test ID
            run_id1: First run ID
            test_id2: Second test ID
            run_id2: Second run ID
            chart_type: Chart type (throughput, latency, strikes, transactions)
            output_dir: Output directory
            
        Returns:
            str: Path to the generated chart file
            
        Raises:
            ValueError: If the chart type is not supported
        """
        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)
        
        # Get the test result summaries
        summary1 = self.get_test_result_summary(test_id1, run_id1)
        summary2 = self.get_test_result_summary(test_id2, run_id2)
        
        # Get the comparison chart generator
        generator = get_chart_generator("comparison")
        if not generator:
            raise ValueError("Comparison chart generator not found")
        
        # Create filename
        filename = os.path.join(output_dir, f"comparison_{test_id1}_{test_id2}_{chart_type}.png")
        
        # Generate comparison chart
        return generator.generate(summary1, summary2, chart_type, filename)
