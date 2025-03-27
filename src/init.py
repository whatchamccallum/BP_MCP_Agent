"""
Initialization Module for Breaking Point MCP Agent
Handles first-time setup and initialization.
"""

import os
import logging
from typing import List, Dict, Any, Optional

from .config import get_config
from .cache import get_cache

logger = logging.getLogger("BPAgent.Init")

def initialize(config_file: Optional[str] = None, create_default_config: bool = True) -> bool:
    """Initialize the Breaking Point MCP Agent
    
    Args:
        config_file: Path to configuration file (default: None, which uses default locations)
        create_default_config: Whether to create a default configuration file if none exists
        
    Returns:
        bool: True if initialization was successful
    """
    # Initialize configuration
    config = get_config()
    config_loaded = config.load(config_file)
    
    # Load environment variables
    config.load_from_env()
    
    # Create default configuration if needed
    if not config_loaded and create_default_config:
        logger.info("Creating default configuration")
        if config.save():
            config_loaded = True
    
    # Setup logging from configuration
    config.setup_logging()
    
    # Initialize cache
    ensure_directories()
    
    # Initialize cache
    cache = get_cache()
    logger.debug("Cache initialized")
    
    # Initialize analyzer plugins
    from .analyzer.plugins.registry import get_plugin_manager
    plugin_manager = get_plugin_manager()
    logger.debug(f"Plugin system initialized with {len(plugin_manager.report_generators)} report generators "
                f"and {len(plugin_manager.chart_generators)} chart generators")
    
    return True

def ensure_directories() -> None:
    """Ensure all required directories exist"""
    config = get_config()
    
    # Cache directory
    cache_config = config.get_cache_config()
    cache_dir = os.path.expanduser(cache_config.get("dir", "~/.bp_agent/cache"))
    os.makedirs(cache_dir, exist_ok=True)
    
    # Logs directory
    log_config = config.get_logging_config()
    log_file = log_config.get("file")
    if log_file:
        log_dir = os.path.dirname(os.path.expanduser(log_file))
        if log_dir:
            os.makedirs(log_dir, exist_ok=True)
    
    # Reports directory
    analyzer_config = config.get_analyzer_config()
    reports_dir = os.path.expanduser(analyzer_config.get("default_output_dir", "./reports"))
    os.makedirs(reports_dir, exist_ok=True)
    
    # Plugin directories
    plugin_dirs = analyzer_config.get("plugin_dirs", [])
    for plugin_dir in plugin_dirs:
        dir_path = os.path.expanduser(plugin_dir)
        if dir_path and not dir_path.startswith("./"):
            os.makedirs(dir_path, exist_ok=True)
