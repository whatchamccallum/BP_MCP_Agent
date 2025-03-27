"""
Unit tests for the cache module
"""

import unittest
import tempfile
import shutil
import time
import os
import sys
import json
from pathlib import Path

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from src.cache import ResultCache

class TestCache(unittest.TestCase):
    """Test cases for the cache module"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Create a temporary directory for the cache
        self.temp_dir = tempfile.mkdtemp()
        self.cache = ResultCache(self.temp_dir, ttl=2)  # Short TTL for testing
        
        # Sample test data
        self.test_id = "test-123"
        self.run_id = "run-456"
        self.test_data = {
            "testName": "Test 1",
            "status": "completed",
            "metrics": {
                "throughput": {
                    "average": 100,
                    "maximum": 120
                }
            }
        }
        
    def tearDown(self):
        """Tear down test fixtures"""
        # Remove the temporary directory
        shutil.rmtree(self.temp_dir)
        
    def test_cache_set_get(self):
        """Test setting and getting cache entries"""
        # Set a cache entry
        self.cache.set(self.test_id, self.run_id, self.test_data)
        
        # Get the cache entry
        cached_data = self.cache.get(self.test_id, self.run_id)
        
        # Check that the data was cached correctly
        self.assertIsNotNone(cached_data)
        self.assertEqual(cached_data["testName"], "Test 1")
        self.assertEqual(cached_data["metrics"]["throughput"]["average"], 100)
        
    def test_cache_expiration(self):
        """Test that cache entries expire after the TTL"""
        # Set a cache entry
        self.cache.set(self.test_id, self.run_id, self.test_data)
        
        # Get the cache entry immediately
        cached_data = self.cache.get(self.test_id, self.run_id)
        self.assertIsNotNone(cached_data)
        
        # Wait for the TTL to expire
        time.sleep(3)
        
        # Try to get the cache entry again
        expired_data = self.cache.get(self.test_id, self.run_id)
        self.assertIsNone(expired_data)
        
    def test_invalidate(self):
        """Test invalidating a cache entry"""
        # Set a cache entry
        self.cache.set(self.test_id, self.run_id, self.test_data)
        
        # Invalidate the cache entry
        success = self.cache.invalidate(self.test_id, self.run_id)
        self.assertTrue(success)
        
        # Try to get the invalidated entry
        cached_data = self.cache.get(self.test_id, self.run_id)
        self.assertIsNone(cached_data)
        
        # Try to invalidate a non-existent entry
        success = self.cache.invalidate("nonexistent", "entry")
        self.assertFalse(success)
        
    def test_clear(self):
        """Test clearing all cache entries"""
        # Set multiple cache entries
        self.cache.set(self.test_id, self.run_id, self.test_data)
        self.cache.set("test2", "run2", {"testName": "Test 2"})
        
        # Clear the cache
        count = self.cache.clear()
        self.assertEqual(count, 2)
        
        # Check that all entries were removed
        self.assertIsNone(self.cache.get(self.test_id, self.run_id))
        self.assertIsNone(self.cache.get("test2", "run2"))
        
    def test_cleanup(self):
        """Test cleaning up expired cache entries"""
        # Set one cache entry with the standard TTL
        self.cache.set(self.test_id, self.run_id, self.test_data)
        
        # Set another entry and manipulate its modification time to make it expired
        other_id = "test2"
        other_run = "run2"
        self.cache.set(other_id, other_run, {"testName": "Test 2"})
        
        # Find the cache file for the second entry
        cache_key = self.cache._get_cache_key(other_id, other_run)
        cache_path = self.cache._get_cache_path(cache_key)
        
        # Set its modification time to the past
        old_time = time.time() - 5  # 5 seconds ago
        os.utime(cache_path, (old_time, old_time))
        
        # Run cleanup
        count = self.cache.cleanup()
        self.assertEqual(count, 1)
        
        # Check that only the expired entry was removed
        self.assertIsNotNone(self.cache.get(self.test_id, self.run_id))
        self.assertIsNone(self.cache.get(other_id, other_run))
        
    def test_get_stats(self):
        """Test getting cache statistics"""
        # Set a cache entry
        self.cache.set(self.test_id, self.run_id, self.test_data)
        
        # Get cache statistics
        stats = self.cache.get_stats()
        
        # Check statistics
        self.assertEqual(stats["entry_count"], 1)
        self.assertGreater(stats["size_bytes"], 0)
        self.assertIsNotNone(stats["newest_entry"])
        
if __name__ == "__main__":
    unittest.main()