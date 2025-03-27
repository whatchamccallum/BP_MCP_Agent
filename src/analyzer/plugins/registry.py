"""
Plugin registry for Breaking Point Analyzer
Handles loading, registering, and managing plugins.
"""

import importlib
import logging
import os
import sys
from typing import Dict, Optional

from .base import (
    PluginManager,
    ReportGenerator,
    ChartGenerator,
    AnalyzerPlugin
)
from .report_generators import (
    StandardReportGenerator,
    ExecutiveReportGenerator,
    DetailedReportGenerator,
    ComplianceReportGenerator
)
from .chart_generators import (
    ThroughputChartGenerator,
    LatencyChartGenerator,
    StrikeChartGenerator,
    TransactionChartGenerator,
    ComparisonChartGenerator
)

logger = logging.getLogger("BPAgent.Analyzer.Plugins")

# Singleton plugin manager instance
_plugin_manager = None

def get_plugin_manager() -> PluginManager:
    """Get the plugin manager instance
    
    Returns:
        PluginManager: Plugin manager singleton
    """
    global _plugin_manager
    
    if _plugin_manager is None:
        _plugin_manager = PluginManager()
        register_default_plugins(_plugin_manager)
        
    return _plugin_manager

def register_default_plugins(manager: PluginManager) -> None:
    """Register the default built-in plugins
    
    Args:
        manager: Plugin manager instance
    """
    # Register report generators
    manager.register_report_generator("standard", StandardReportGenerator())
    manager.register_report_generator("executive", ExecutiveReportGenerator())
    manager.register_report_generator("detailed", DetailedReportGenerator())
    manager.register_report_generator("compliance", ComplianceReportGenerator())
    
    # Register chart generators
    manager.register_chart_generator("throughput", ThroughputChartGenerator())
    manager.register_chart_generator("latency", LatencyChartGenerator())
    manager.register_chart_generator("strikes", StrikeChartGenerator())
    manager.register_chart_generator("transactions", TransactionChartGenerator())
    manager.register_chart_generator("comparison", ComparisonChartGenerator())
    
    logger.debug("Registered default plugins")

def discover_plugins(plugin_dirs: Optional[list[str]] = None) -> None:
    """Discover and load plugins from directories
    
    Args:
        plugin_dirs: List of directories to search for plugins
                    (default: None, which uses the built-in plugins only)
    """
    if not plugin_dirs:
        return
    
    manager = get_plugin_manager()
    
    for plugin_dir in plugin_dirs:
        if not os.path.isdir(plugin_dir):
            logger.warning(f"Plugin directory not found: {plugin_dir}")
            continue
        
        # Add the plugin directory to the Python path
        if plugin_dir not in sys.path:
            sys.path.insert(0, plugin_dir)
        
        # Find all Python modules in the directory
        for filename in os.listdir(plugin_dir):
            if filename.endswith(".py") and not filename.startswith("_"):
                module_name = filename[:-3]  # Remove .py extension
                
                try:
                    # Import the module
                    module = importlib.import_module(module_name)
                    
                    # Look for plugin registration function
                    if hasattr(module, "register_plugins"):
                        module.register_plugins(manager)
                        logger.info(f"Loaded plugins from module: {module_name}")
                except Exception as e:
                    logger.error(f"Error loading plugin module {module_name}: {e}")

def get_report_generator(name: str) -> Optional[ReportGenerator]:
    """Get a report generator by name
    
    Args:
        name: Generator name
        
    Returns:
        Optional[ReportGenerator]: Report generator or None if not found
    """
    return get_plugin_manager().get_report_generator(name)

def get_chart_generator(name: str) -> Optional[ChartGenerator]:
    """Get a chart generator by name
    
    Args:
        name: Generator name
        
    Returns:
        Optional[ChartGenerator]: Chart generator or None if not found
    """
    return get_plugin_manager().get_chart_generator(name)

def get_analyzer(name: str) -> Optional[AnalyzerPlugin]:
    """Get an analyzer by name
    
    Args:
        name: Analyzer name
        
    Returns:
        Optional[AnalyzerPlugin]: Analyzer or None if not found
    """
    return get_plugin_manager().get_analyzer(name)
