"""
Configuration Management Module
Handles loading, validating, and accessing configuration settings
"""

import os
import yaml
import logging
import argparse
from typing import Dict, Any, Optional
from pathlib import Path

logger = logging.getLogger("BPAgent.Config")

# Default configuration values
DEFAULT_CONFIG = {
    "api": {
        "host": "localhost",
        "timeout": 60,
        "verify_ssl": False,
        "retries": 3,
        "retry_delay": 5
    },
    "cache": {
        "enabled": True,
        "ttl": 3600,  # 1 hour in seconds
        "dir": "~/.bp_agent/cache",
        "compression": False
    },
    "analyzer": {
        "default_report_type": "standard",
        "default_output_format": "html",
        "default_output_dir": "./reports",
        "plugin_dirs": []
    },
    "logging": {
        "level": "INFO",
        "file": "~/.bp_agent/logs/agent.log",
        "max_size": 10485760,  # 10 MB
        "backup_count": 5,
        "console": True
    }
}

class Config:
    """Configuration management class for Breaking Point MCP Agent"""
    
    def __init__(self):
        self._config = DEFAULT_CONFIG.copy()
        self._config_file = None
        self._env_prefix = "BP_AGENT_"
    
    def load(self, config_file: Optional[str] = None) -> bool:
        """Load configuration from file
        
        Args:
            config_file: Path to configuration file (default: None, which uses default locations)
            
        Returns:
            bool: True if configuration was loaded successfully
        """
        if config_file:
            # Use specified config file
            config_paths = [config_file]
        else:
            # Try default locations
            config_paths = [
                "./config.yaml",
                "./config.yml",
                "~/.bp_agent/config.yaml",
                "/etc/bp_agent/config.yaml"
            ]
        
        # Try loading from each path
        for path in config_paths:
            expanded_path = os.path.expanduser(path)
            if os.path.exists(expanded_path):
                try:
                    with open(expanded_path, 'r') as f:
                        file_config = yaml.safe_load(f)
                        if file_config:
                            self._update_config(file_config)
                            self._config_file = expanded_path
                            logger.info(f"Loaded configuration from {expanded_path}")
                            return True
                except Exception as e:
                    logger.warning(f"Error loading config from {expanded_path}: {e}")
        
        logger.info("No configuration file found, using defaults")
        return False
    
    def _update_config(self, new_config: Dict[str, Any], base: Optional[Dict[str, Any]] = None, 
                      path: str = "") -> None:
        """Recursively update configuration
        
        Args:
            new_config: New configuration values
            base: Base configuration to update (default: None, which uses root config)
            path: Current path in the configuration (for logging)
        """
        if base is None:
            base = self._config
            
        for key, value in new_config.items():
            current_path = f"{path}.{key}" if path else key
            
            if isinstance(value, dict) and key in base and isinstance(base[key], dict):
                # Recursively update nested dictionaries
                self._update_config(value, base[key], current_path)
            else:
                # Update value
                base[key] = value
                logger.debug(f"Updated config {current_path} = {value}")
    
    def load_from_env(self) -> None:
        """Load configuration from environment variables
        
        Environment variables should be in the format:
        BP_AGENT_SECTION_KEY=value
        
        For example:
        BP_AGENT_API_HOST=breaking-point.example.com
        """
        for var_name, var_value in os.environ.items():
            if var_name.startswith(self._env_prefix):
                # Remove prefix and split into parts
                config_path = var_name[len(self._env_prefix):].lower().split('_')
                
                if len(config_path) < 2:
                    continue
                    
                # Navigate to the right section
                section = config_path[0]
                key = config_path[1]
                
                # Handle nested variables with more than 2 levels
                if len(config_path) > 2:
                    key = '_'.join(config_path[1:])
                
                if section in self._config:
                    if key in self._config[section]:
                        # Convert value to the right type
                        orig_value = self._config[section][key]
                        if isinstance(orig_value, bool):
                            # Convert string to boolean
                            self._config[section][key] = var_value.lower() in ('true', 't', 'yes', 'y', '1')
                        elif isinstance(orig_value, int):
                            # Convert string to integer
                            try:
                                self._config[section][key] = int(var_value)
                            except ValueError:
                                logger.warning(f"Invalid integer value for {var_name}: {var_value}")
                        elif isinstance(orig_value, float):
                            # Convert string to float
                            try:
                                self._config[section][key] = float(var_value)
                            except ValueError:
                                logger.warning(f"Invalid float value for {var_name}: {var_value}")
                        else:
                            # Use string value
                            self._config[section][key] = var_value
                        
                        logger.debug(f"Set {section}.{key} from environment variable {var_name}")
    
    def load_from_args(self, args: argparse.Namespace) -> None:
        """Load configuration from command line arguments
        
        Args:
            args: Parsed command line arguments
        """
        # Map argument names to config paths
        arg_mapping = {
            "host": ("api", "host"),
            "timeout": ("api", "timeout"),
            "verify_ssl": ("api", "verify_ssl"),
            "cache": ("cache", "enabled"),
            "cache_ttl": ("cache", "ttl"),
            "cache_dir": ("cache", "dir"),
            "output_dir": ("analyzer", "default_output_dir"),
            "report_type": ("analyzer", "default_report_type"),
            "output_format": ("analyzer", "default_output_format"),
            "log_level": ("logging", "level"),
            "log_file": ("logging", "file")
        }
        
        # Update config from args
        for arg_name, config_path in arg_mapping.items():
            if hasattr(args, arg_name) and getattr(args, arg_name) is not None:
                section, key = config_path
                value = getattr(args, arg_name)
                self._config[section][key] = value
                logger.debug(f"Set {section}.{key} from command line argument --{arg_name}")
    
    def save(self, filename: Optional[str] = None) -> bool:
        """Save current configuration to file
        
        Args:
            filename: Path to save configuration to (default: None, which uses the loaded file)
            
        Returns:
            bool: True if configuration was saved successfully
        """
        save_path = filename or self._config_file
        
        if not save_path:
            save_path = os.path.expanduser("~/.bp_agent/config.yaml")
            # Ensure directory exists
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
        
        try:
            with open(save_path, 'w') as f:
                yaml.dump(self._config, f, default_flow_style=False)
            logger.info(f"Saved configuration to {save_path}")
            return True
        except Exception as e:
            logger.error(f"Error saving configuration to {save_path}: {e}")
            return False
    
    def get(self, section: str, key: str, default: Any = None) -> Any:
        """Get configuration value
        
        Args:
            section: Configuration section
            key: Configuration key
            default: Default value if not found
            
        Returns:
            Any: Configuration value or default
        """
        if section in self._config and key in self._config[section]:
            return self._config[section][key]
        return default
    
    def set(self, section: str, key: str, value: Any) -> None:
        """Set configuration value
        
        Args:
            section: Configuration section
            key: Configuration key
            value: Value to set
        """
        if section not in self._config:
            self._config[section] = {}
        self._config[section][key] = value
    
    def get_api_config(self) -> Dict[str, Any]:
        """Get API configuration
        
        Returns:
            Dict[str, Any]: API configuration
        """
        return self._config.get("api", {})
    
    def get_cache_config(self) -> Dict[str, Any]:
        """Get cache configuration
        
        Returns:
            Dict[str, Any]: Cache configuration
        """
        return self._config.get("cache", {})
    
    def get_analyzer_config(self) -> Dict[str, Any]:
        """Get analyzer configuration
        
        Returns:
            Dict[str, Any]: Analyzer configuration
        """
        return self._config.get("analyzer", {})
    
    def get_logging_config(self) -> Dict[str, Any]:
        """Get logging configuration
        
        Returns:
            Dict[str, Any]: Logging configuration
        """
        return self._config.get("logging", {})
    
    def get_credentials(self) -> Dict[str, str]:
        """Get API credentials
        
        Returns:
            Dict[str, str]: Credentials (username, password)
        """
        # Try to get from environment variables first (more secure)
        username = os.environ.get(f"{self._env_prefix}USERNAME")
        password = os.environ.get(f"{self._env_prefix}PASSWORD")
        
        # Fall back to config file
        if not username or not password:
            credentials = self._config.get("credentials", {})
            username = username or credentials.get("username")
            password = password or credentials.get("password")
        
        return {
            "username": username,
            "password": password
        }
    
    def setup_logging(self) -> None:
        """Configure logging based on current settings"""
        log_config = self.get_logging_config()
        
        # Set root logger level
        log_level = getattr(logging, log_config.get("level", "INFO"), logging.INFO)
        root_logger = logging.getLogger()
        root_logger.setLevel(log_level)
        
        # Clear any existing handlers
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)
        
        # Configure console logging
        if log_config.get("console", True):
            console_handler = logging.StreamHandler()
            console_handler.setLevel(log_level)
            formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(name)s: %(message)s')
            console_handler.setFormatter(formatter)
            root_logger.addHandler(console_handler)
        
        # Configure file logging
        log_file = log_config.get("file")
        if log_file:
            try:
                # Expand user directory if present
                log_file = os.path.expanduser(log_file)
                
                # Ensure log directory exists
                log_dir = os.path.dirname(log_file)
                if log_dir:
                    os.makedirs(log_dir, exist_ok=True)
                
                # Use rotating file handler for log rotation
                from logging.handlers import RotatingFileHandler
                file_handler = RotatingFileHandler(
                    log_file,
                    maxBytes=log_config.get("max_size", 10485760),
                    backupCount=log_config.get("backup_count", 5)
                )
                file_handler.setLevel(log_level)
                formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(name)s: %(message)s')
                file_handler.setFormatter(formatter)
                root_logger.addHandler(file_handler)
                
                logger.debug(f"Configured logging to file: {log_file}")
            except Exception as e:
                logger.error(f"Failed to configure file logging: {e}")

# Singleton instance
_config_instance = None

def get_config() -> Config:
    """Get the configuration instance
    
    Returns:
        Config: Configuration instance
    """
    global _config_instance
    if _config_instance is None:
        _config_instance = Config()
    return _config_instance
