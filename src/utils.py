"""
Utility functions for the Breaking Point MCP Agent
This module provides common utility functions used across the project.
"""

import os
import logging
import json
import yaml
from typing import Dict, Any, List, Optional, Union

logger = logging.getLogger("BPAgent.Utils")

def configure_logging(
    level: int = logging.INFO,
    log_file: Optional[str] = None,
    console: bool = True,
    file_level: Optional[int] = None
) -> None:
    """Configure logging for the Breaking Point MCP Agent

    Args:
        level: Logging level for the root logger
        log_file: Path to log file (if None, file logging is disabled)
        console: Whether to enable console logging
        file_level: Logging level for the file handler (defaults to the same as level)
    """
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    
    # Clear existing handlers
    root_logger.handlers = []
    
    # Create formatters
    console_formatter = logging.Formatter('%(levelname)s: %(message)s')
    file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # Create console handler
    if console:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(level)
        console_handler.setFormatter(console_formatter)
        root_logger.addHandler(console_handler)
    
    # Create file handler
    if log_file:
        os.makedirs(os.path.dirname(os.path.abspath(log_file)), exist_ok=True)
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(file_level or level)
        file_handler.setFormatter(file_formatter)
        root_logger.addHandler(file_handler)
    
    # Configure library loggers to be less verbose
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.getLogger("matplotlib").setLevel(logging.WARNING)

def load_config(config_path: str) -> Dict[str, Any]:
    """Load configuration from a JSON or YAML file

    Args:
        config_path: Path to the configuration file

    Returns:
        Dict: Configuration data

    Raises:
        ValueError: If the file format is not supported
        FileNotFoundError: If the file does not exist
    """
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
    
    file_ext = os.path.splitext(config_path)[1].lower()
    
    with open(config_path, 'r') as f:
        if file_ext in ['.yaml', '.yml']:
            return yaml.safe_load(f)
        elif file_ext == '.json':
            return json.load(f)
        else:
            raise ValueError(f"Unsupported configuration file format: {file_ext}")

def save_config(config: Dict[str, Any], config_path: str) -> None:
    """Save configuration to a JSON or YAML file

    Args:
        config: Configuration data
        config_path: Path to the configuration file

    Raises:
        ValueError: If the file format is not supported
    """
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(os.path.abspath(config_path)), exist_ok=True)
    
    file_ext = os.path.splitext(config_path)[1].lower()
    
    with open(config_path, 'w') as f:
        if file_ext in ['.yaml', '.yml']:
            yaml.dump(config, f, default_flow_style=False)
        elif file_ext == '.json':
            json.dump(config, f, indent=2)
        else:
            raise ValueError(f"Unsupported configuration file format: {file_ext}")

def is_valid_ip(ip: str) -> bool:
    """Check if a string is a valid IP address

    Args:
        ip: String to check

    Returns:
        bool: True if the string is a valid IP address, False otherwise
    """
    try:
        parts = ip.split('.')
        if len(parts) != 4:
            return False
        
        for part in parts:
            num = int(part)
            if num < 0 or num > 255:
                return False
                
        return True
    except (ValueError, AttributeError):
        return False

def is_valid_cidr(cidr: str) -> bool:
    """Check if a string is a valid CIDR notation

    Args:
        cidr: String to check (e.g., "192.168.1.0/24")

    Returns:
        bool: True if the string is a valid CIDR notation, False otherwise
    """
    if not cidr or '/' not in cidr:
        return False
        
    try:
        ip_part, mask_part = cidr.split('/')
        
        # Check IP part
        if not is_valid_ip(ip_part):
            return False
            
        # Check mask part
        mask = int(mask_part)
        if mask < 0 or mask > 32:
            return False
            
        return True
    except (ValueError, AttributeError):
        return False

def format_bytes(bytes: int) -> str:
    """Format bytes into a human-readable string

    Args:
        bytes: Number of bytes

    Returns:
        str: Formatted string (e.g., "1.23 MB")
    """
    suffixes = ['B', 'KB', 'MB', 'GB', 'TB', 'PB']
    i = 0
    while bytes >= 1024 and i < len(suffixes) - 1:
        bytes /= 1024
        i += 1
    
    return f"{bytes:.2f} {suffixes[i]}"

def format_duration(seconds: int) -> str:
    """Format duration in seconds into a human-readable string

    Args:
        seconds: Duration in seconds

    Returns:
        str: Formatted string (e.g., "1h 23m 45s")
    """
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    
    parts = []
    if hours > 0:
        parts.append(f"{hours}h")
    if minutes > 0 or hours > 0:
        parts.append(f"{minutes}m")
    parts.append(f"{seconds}s")
    
    return " ".join(parts)

def merge_dicts(dict1: Dict[str, Any], dict2: Dict[str, Any]) -> Dict[str, Any]:
    """Recursively merge two dictionaries

    Args:
        dict1: First dictionary
        dict2: Second dictionary (overrides dict1 on conflicts)

    Returns:
        Dict: Merged dictionary
    """
    result = dict1.copy()
    
    for key, value in dict2.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = merge_dicts(result[key], value)
        else:
            result[key] = value
    
    return result

def safe_get(data: Dict[str, Any], *keys: str, default: Any = None) -> Any:
    """Safely get a nested value from a dictionary

    Args:
        data: Dictionary to get value from
        *keys: Keys to navigate the nested structure
        default: Default value if not found

    Returns:
        Any: Value or default if not found
    """
    current = data
    
    for key in keys:
        if not isinstance(current, dict) or key not in current:
            return default
        current = current[key]
    
    return current
