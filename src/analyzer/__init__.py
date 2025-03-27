"""
Breaking Point Test Result Analyzer
This package provides analyzer functionality for Breaking Point test results
"""

from .plugins.registry import get_plugin_manager, discover_plugins
from .core import TestResultAnalyzer

# Initialize the plugin manager
get_plugin_manager()

__all__ = ['TestResultAnalyzer', 'discover_plugins']
