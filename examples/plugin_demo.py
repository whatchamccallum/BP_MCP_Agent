#!/usr/bin/env python
"""
Demo of the plugin-based architecture for Breaking Point MCP Agent
"""

import os
import sys
import logging
from typing import Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
logger = logging.getLogger("PluginDemo")

# Add the parent directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.analyzer.plugins.registry import get_plugin_manager, discover_plugins
from src.analyzer import TestResultAnalyzer
from src.api import BreakingPointAPI

def create_test_summary() -> Dict[str, Any]:
    """Create a fake test summary for demo purposes
    
    Returns:
        Dict[str, Any]: Test summary dictionary
    """
    return {
        "testId": "test123",
        "runId": "run456",
        "testName": "Demo Test",
        "testType": "appsim",
        "startTime": "2023-04-01T10:00:00Z",
        "endTime": "2023-04-01T11:00:00Z",
        "duration": 3600,
        "status": "completed",
        "metrics": {
            "throughput": {
                "average": 1250.5,
                "maximum": 1500.2,
                "unit": "mbps"
            },
            "latency": {
                "average": 12.3,
                "maximum": 45.6,
                "unit": "ms"
            },
            "transactions": {
                "attempted": 10000,
                "successful": 9850,
                "failed": 150,
                "successRate": 98.5
            }
        }
    }

def main():
    """Main demo function"""
    # Create output directory
    output_dir = os.path.join(os.path.dirname(__file__), "output")
    os.makedirs(output_dir, exist_ok=True)
    
    logger.info("==== Breaking Point MCP Agent Plugin Demo ====")
    
    # Get the plugin manager and show the default plugins
    plugin_manager = get_plugin_manager()
    
    logger.info("Available report generators:")
    for name in plugin_manager.report_generators:
        logger.info(f"  - {name}")
    
    logger.info("Available chart generators:")
    for name in plugin_manager.chart_generators:
        logger.info(f"  - {name}")
    
    # Discover and load external plugins
    plugin_dir = os.path.join(os.path.dirname(__file__), "plugins")
    logger.info(f"Discovering plugins in: {plugin_dir}")
    discover_plugins([plugin_dir])
    
    # Show updated plugin list
    logger.info("Updated report generators after discovery:")
    for name in plugin_manager.report_generators:
        logger.info(f"  - {name}")
    
    # Create a test summary
    summary = create_test_summary()
    logger.info(f"Created test summary for '{summary['testName']}'")
    
    # Generate reports using different plugins
    report_types = ["standard", "executive", "detailed", "custom"]
    
    for report_type in report_types:
        try:
            generator = plugin_manager.get_report_generator(report_type)
            if generator:
                output_file = os.path.join(output_dir, f"demo_{report_type}_report")
                if report_type == "custom":
                    output_format = "txt"
                else:
                    output_format = "html"
                
                output_path = generator.generate(summary, {}, output_format, output_file)
                logger.info(f"Generated {report_type} report: {output_path}")
            else:
                logger.warning(f"Report generator '{report_type}' not found")
        except Exception as e:
            logger.error(f"Error generating {report_type} report: {e}")
    
    # Generate charts
    chart_types = ["throughput", "latency"]
    
    for chart_type in chart_types:
        try:
            generator = plugin_manager.get_chart_generator(chart_type)
            if generator:
                output_file = os.path.join(output_dir, f"demo_{chart_type}_chart.png")
                output_path = generator.generate(summary, {}, output_file)
                logger.info(f"Generated {chart_type} chart: {output_path}")
            else:
                logger.warning(f"Chart generator '{chart_type}' not found")
        except Exception as e:
            logger.error(f"Error generating {chart_type} chart: {e}")
    
    # Generate transaction chart if metrics exist
    if "transactions" in summary.get("metrics", {}):
        try:
            generator = plugin_manager.get_chart_generator("transactions")
            if generator:
                output_file = os.path.join(output_dir, f"demo_transactions_chart.png")
                output_path = generator.generate(summary, {}, output_file)
                logger.info(f"Generated transactions chart: {output_path}")
        except Exception as e:
            logger.error(f"Error generating transactions chart: {e}")
    
    logger.info("Plugin demo completed!")

if __name__ == "__main__":
    main()
