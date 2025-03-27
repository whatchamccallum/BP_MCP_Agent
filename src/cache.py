"""
Cache Module for Breaking Point MCP Agent
Provides caching functionality for test results to improve performance.
"""

import os
import json
import time
import hashlib
import logging
import gzip
import traceback
from typing import Dict, Any, Optional, Tuple
from datetime import datetime, timedelta

from .config import get_config
from .exceptions import CacheError
from .error_handler import ErrorContext

# Configure module logger
logger = logging.getLogger("BPAgent.Cache")

class ResultCache:
    """Caches test results to avoid repeated API calls"""
    
    def __init__(self, cache_dir: Optional[str] = None, ttl: Optional[int] = None, 
                compression: Optional[bool] = None):
        """Initialize the result cache
        
        Args:
            cache_dir: Directory to store cache files (default: from config)
            ttl: Cache time-to-live in seconds (default: from config)
            compression: Whether to compress cached data (default: from config)
        """
        # Get configuration
        config = get_config()
        cache_config = config.get_cache_config()
        
        # Set attributes from parameters or config
        self.cache_dir = cache_dir or os.path.expanduser(cache_config.get("dir", "~/.bp_agent/cache"))
        self.ttl = ttl or cache_config.get("ttl", 3600)
        self.compression = compression if compression is not None else cache_config.get("compression", False)
        
        # Create cache directory if it doesn't exist
        os.makedirs(self.cache_dir, exist_ok=True)
        logger.debug(f"Initialized result cache in {self.cache_dir} with TTL {self.ttl}s" + 
                    f" (compression: {'enabled' if self.compression else 'disabled'})")
        
    def _get_cache_key(self, test_id: str, run_id: str) -> str:
        """Generate a cache key for a test result
        
        Args:
            test_id: Test ID
            run_id: Run ID
            
        Returns:
            str: Cache key
        """
        key = f"{test_id}_{run_id}"
        return hashlib.md5(key.encode()).hexdigest()
        
    def _get_cache_path(self, cache_key: str) -> str:
        """Get the path to a cache file
        
        Args:
            cache_key: Cache key
            
        Returns:
            str: Path to cache file
        """
        ext = ".json.gz" if self.compression else ".json"
        return os.path.join(self.cache_dir, f"{cache_key}{ext}")
        
    def get(self, test_id: str, run_id: str) -> Optional[Dict]:
        """Get a cached test result
        
        Args:
            test_id: Test ID
            run_id: Run ID
            
        Returns:
            Optional[Dict]: Cached test result or None if not found or expired
        """
        context_info = {
            "test_id": test_id,
            "run_id": run_id,
            "operation": "get",
            "cache_dir": self.cache_dir
        }
        
        with ErrorContext(context_info, CacheError, "CACHE_READ_ERROR"):
            cache_key = self._get_cache_key(test_id, run_id)
            
            # Try both compressed and uncompressed paths (for backward compatibility)
            cache_paths = [
                os.path.join(self.cache_dir, f"{cache_key}.json.gz"),
                os.path.join(self.cache_dir, f"{cache_key}.json")
            ]
            
            for cache_path in cache_paths:
                if os.path.exists(cache_path):
                    try:
                        # Check if cache is expired
                        file_age = time.time() - os.path.getmtime(cache_path)
                        if file_age > self.ttl:
                            logger.debug(f"Cache expired for {test_id}, {run_id} (age: {file_age:.1f}s)")
                            return None
                        
                        # Read cache file
                        if cache_path.endswith('.gz'):
                            with gzip.open(cache_path, 'rt', encoding='utf-8') as f:
                                cached_data = json.load(f)
                        else:
                            with open(cache_path, 'r') as f:
                                cached_data = json.load(f)
                        
                        logger.debug(f"Cache hit for {test_id}, {run_id}")
                        return cached_data
                        
                    except json.JSONDecodeError as e:
                        # Invalid JSON in cache file
                        logger.warning(f"Invalid JSON in cache file {cache_path}: {e}")
                        try:
                            # Attempt to remove the corrupted file
                            os.remove(cache_path)
                            logger.info(f"Removed corrupted cache file: {cache_path}")
                        except Exception as rm_e:
                            logger.warning(f"Could not remove corrupted cache file: {rm_e}")
                        return None
                        
                    except Exception as e:
                        logger.warning(f"Error reading cache for {test_id}, {run_id}: {e}")
                        logger.debug(f"Cache error traceback: {traceback.format_exc()}")
                        return None
            
            logger.debug(f"Cache miss: No cache file for {test_id}, {run_id}")
            return None
            
    def set(self, test_id: str, run_id: str, data: Dict) -> bool:
        """Store a test result in the cache
        
        Args:
            test_id: Test ID
            run_id: Run ID
            data: Test result data
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not data:
            logger.warning(f"Attempted to cache empty data for {test_id}, {run_id}")
            return False
            
        context_info = {
            "test_id": test_id,
            "run_id": run_id,
            "operation": "set",
            "cache_dir": self.cache_dir,
            "compression": self.compression
        }
        
        with ErrorContext(context_info, CacheError, "CACHE_WRITE_ERROR"):
            cache_key = self._get_cache_key(test_id, run_id)
            cache_path = self._get_cache_path(cache_key)
            
            # Ensure cache directory exists
            os.makedirs(os.path.dirname(cache_path), exist_ok=True)
            
            try:
                # Create a temporary file first to avoid corruption if interrupted
                temp_path = f"{cache_path}.tmp"
                
                # Write to temporary file
                if self.compression:
                    with gzip.open(temp_path, 'wt', encoding='utf-8') as f:
                        json.dump(data, f)
                else:
                    with open(temp_path, 'w') as f:
                        json.dump(data, f)
                
                # Rename to final path (atomic operation)
                os.replace(temp_path, cache_path)
                
                logger.debug(f"Cached result for {test_id}, {run_id}")
                return True
                
            except json.JSONEncodeError as e:
                logger.error(f"Failed to encode data as JSON for {test_id}, {run_id}: {e}")
                return False
                
            except Exception as e:
                logger.warning(f"Error writing cache for {test_id}, {run_id}: {e}")
                logger.debug(f"Cache error traceback: {traceback.format_exc()}")
                
                # Clean up temporary file if it exists
                try:
                    if os.path.exists(temp_path):
                        os.remove(temp_path)
                except Exception:
                    pass
                    
                return False
            
    def invalidate(self, test_id: str, run_id: str) -> bool:
        """Invalidate a cached test result
        
        Args:
            test_id: Test ID
            run_id: Run ID
            
        Returns:
            bool: True if cache was invalidated, False otherwise
        """
        cache_key = self._get_cache_key(test_id, run_id)
        
        # Try both compressed and uncompressed paths
        cache_paths = [
            os.path.join(self.cache_dir, f"{cache_key}.json.gz"),
            os.path.join(self.cache_dir, f"{cache_key}.json")
        ]
        
        success = False
        for cache_path in cache_paths:
            if os.path.exists(cache_path):
                try:
                    os.remove(cache_path)
                    logger.debug(f"Invalidated cache at {cache_path}")
                    success = True
                except Exception as e:
                    logger.warning(f"Error invalidating cache at {cache_path}: {e}")
                    
        if success:
            logger.debug(f"Invalidated cache for {test_id}, {run_id}")
            
        return success
        
    def clear(self) -> int:
        """Clear all cached test results
        
        Returns:
            int: Number of cache entries cleared
        """
        count = 0
        for filename in os.listdir(self.cache_dir):
            if filename.endswith(".json") or filename.endswith(".json.gz"):
                try:
                    os.remove(os.path.join(self.cache_dir, filename))
                    count += 1
                except Exception as e:
                    logger.warning(f"Error removing cache file {filename}: {e}")
                    
        logger.info(f"Cleared {count} cache entries")
        return count
        
    def get_stats(self) -> Dict:
        """Get cache statistics
        
        Returns:
            Dict: Cache statistics
        """
        stats = {
            "cache_dir": self.cache_dir,
            "ttl": self.ttl,
            "compression": self.compression,
            "entry_count": 0,
            "size_bytes": 0,
            "oldest_entry": None,
            "newest_entry": None
        }
        
        oldest_time = float('inf')
        newest_time = 0
        
        for filename in os.listdir(self.cache_dir):
            if filename.endswith(".json") or filename.endswith(".json.gz"):
                file_path = os.path.join(self.cache_dir, filename)
                stats["entry_count"] += 1
                
                try:
                    file_size = os.path.getsize(file_path)
                    stats["size_bytes"] += file_size
                    
                    mtime = os.path.getmtime(file_path)
                    if mtime < oldest_time:
                        oldest_time = mtime
                        stats["oldest_entry"] = datetime.fromtimestamp(mtime).isoformat()
                        
                    if mtime > newest_time:
                        newest_time = mtime
                        stats["newest_entry"] = datetime.fromtimestamp(mtime).isoformat()
                        
                except Exception as e:
                    logger.warning(f"Error getting stats for {filename}: {e}")
                    
        # Format size for human readability
        if stats["size_bytes"] > 1024 * 1024:
            stats["size_human"] = f"{stats['size_bytes'] / (1024 * 1024):.2f} MB"
        elif stats["size_bytes"] > 1024:
            stats["size_human"] = f"{stats['size_bytes'] / 1024:.2f} KB"
        else:
            stats["size_human"] = f"{stats['size_bytes']} bytes"
            
        return stats
        
    def cleanup(self, max_age: Optional[int] = None) -> int:
        """Clean up expired cache entries
        
        Args:
            max_age: Maximum age in seconds (default: self.ttl)
            
        Returns:
            int: Number of entries removed
        """
        max_age = max_age or self.ttl
        count = 0
        now = time.time()
        
        for filename in os.listdir(self.cache_dir):
            if filename.endswith(".json") or filename.endswith(".json.gz"):
                file_path = os.path.join(self.cache_dir, filename)
                
                try:
                    file_age = now - os.path.getmtime(file_path)
                    if file_age > max_age:
                        os.remove(file_path)
                        count += 1
                except Exception as e:
                    logger.warning(f"Error cleaning up {filename}: {e}")
                    
        logger.info(f"Cleaned up {count} expired cache entries")
        return count

# Singleton cache instance
_cache_instance = None

def get_cache(cache_dir: Optional[str] = None, ttl: Optional[int] = None,
             compression: Optional[bool] = None) -> ResultCache:
    """Get the cache instance (singleton)
    
    Args:
        cache_dir: Directory to store cache files (default: from config)
        ttl: Cache time-to-live in seconds (default: from config)
        compression: Whether to compress cached data (default: from config)
        
    Returns:
        ResultCache: Cache instance
    """
    global _cache_instance
    
    # Get configuration
    config = get_config()
    cache_config = config.get_cache_config()
    
    # Check if cache is enabled
    cache_enabled = cache_config.get("enabled", True)
    if not cache_enabled:
        logger.info("Cache is disabled in configuration")
        # Return a dummy cache that doesn't actually cache anything
        class DummyCache:
            def get(self, *args, **kwargs): return None
            def set(self, *args, **kwargs): return True
            def invalidate(self, *args, **kwargs): return True
            def clear(self, *args, **kwargs): return 0
            def get_stats(self, *args, **kwargs): return {"disabled": True}
            def cleanup(self, *args, **kwargs): return 0
        return DummyCache()
    
    # Create cache instance if needed
    if _cache_instance is None:
        _cache_instance = ResultCache(cache_dir, ttl, compression)
        
    return _cache_instance
