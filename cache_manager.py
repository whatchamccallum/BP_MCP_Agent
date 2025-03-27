#!/usr/bin/env python
"""
Breaking Point Cache Management Tool
A utility script to manage the test result cache.
"""

import sys
import os
import argparse
import logging
from datetime import datetime, timedelta

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from src.cache import get_cache
from src.utils import configure_logging
from src.constants import DEFAULT_CACHE_DIR, DEFAULT_CACHE_TTL

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Breaking Point Cache Manager")
    parser.add_argument("--cache-dir", type=str, default=DEFAULT_CACHE_DIR,
                      help=f"Cache directory (default: {DEFAULT_CACHE_DIR})")
    parser.add_argument("--cache-ttl", type=int, default=DEFAULT_CACHE_TTL,
                      help=f"Cache time-to-live in seconds (default: {DEFAULT_CACHE_TTL})")
    parser.add_argument("--log-file", default="cache_manager.log", help="Log file path")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    
    # Cache operations
    actions = parser.add_mutually_exclusive_group(required=True)
    actions.add_argument("--stats", action="store_true", help="Show cache statistics")
    actions.add_argument("--clear", action="store_true", help="Clear all cache entries")
    actions.add_argument("--cleanup", action="store_true", help="Remove expired cache entries")
    actions.add_argument("--invalidate", metavar=("TEST_ID", "RUN_ID"), nargs=2,
                       help="Invalidate a specific test result")
    actions.add_argument("--max-age", type=int, help="Remove entries older than specified seconds")
    
    args = parser.parse_args()
    
    # Configure logging
    log_dir = os.path.dirname(args.log_file)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir, exist_ok=True)
        
    configure_logging(
        level=logging.DEBUG if args.debug else logging.INFO,
        log_file=args.log_file
    )
    
    logger = logging.getLogger("CacheManager")
    
    # Get cache instance
    cache = get_cache(args.cache_dir, args.cache_ttl)
    
    # Perform requested action
    try:
        if args.stats:
            stats = cache.get_stats()
            print(f"Cache Statistics:")
            print(f"  Location: {stats['cache_dir']}")
            print(f"  Entries: {stats['entry_count']}")
            print(f"  Size: {stats['size_human']}")
            print(f"  Oldest entry: {stats['oldest_entry'] or 'None'}")
            print(f"  Newest entry: {stats['newest_entry'] or 'None'}")
            print(f"  TTL: {stats['ttl']} seconds")
            
        elif args.clear:
            count = cache.clear()
            logger.info(f"Cleared {count} cache entries")
            print(f"Cleared {count} cache entries")
            
        elif args.cleanup:
            count = cache.cleanup()
            logger.info(f"Cleaned up {count} expired cache entries")
            print(f"Cleaned up {count} expired cache entries")
            
        elif args.invalidate:
            test_id, run_id = args.invalidate
            success = cache.invalidate(test_id, run_id)
            if success:
                logger.info(f"Invalidated cache for test {test_id}, run {run_id}")
                print(f"Invalidated cache for test {test_id}, run {run_id}")
            else:
                logger.info(f"No cache found for test {test_id}, run {run_id}")
                print(f"No cache found for test {test_id}, run {run_id}")
                
        elif args.max_age is not None:
            count = cache.cleanup(args.max_age)
            logger.info(f"Removed {count} cache entries older than {args.max_age} seconds")
            print(f"Removed {count} cache entries older than {args.max_age} seconds")
            
    except Exception as e:
        logger.error(f"Error: {e}")
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()