#!/usr/bin/env python
"""
Integration tests for Breaking Point MCP Agent
Tests the complete workflow from API connection to report generation
"""

import os
import sys
import time
import asyncio
import logging
import argparse
import unittest
from unittest import mock
from typing import Dict, Any, List, Optional, Tuple

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
logger = logging.getLogger("BPAgent.IntegrationTest")

# Add the current directory to the path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Import the Breaking Point MCP Agent modules
from src.config import get_config, Config
from src.init import initialize
from src.api import create_api, BreakingPointAPI
from src.api_async import AsyncBreakingPointAPI
from src.analyzer import get_test_result_summary, generate_report, generate_charts
from src.analyzer_async import get_test_result_summary as async_get_test_result_summary
from src.cache import get_cache
from src.exceptions import BPError, APIError, AuthenticationError

# Mock responses for tests
MOCK_TEST_LIST = [
    {"id": "test1", "name": "Test 1", "type": "strike"},
    {"id": "test2", "name": "Test 2", "type": "appsim"},
    {"id": "test3", "name": "Test 3", "type": "bandwidth"}
]

MOCK_TEST_RESULT = {
    "testId": "test1",
    "runId": "run1",
    "testName": "Test 1",
    "testType": "strike",
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
        "strikes": {
            "attempted": 1000,
            "blocked": 950,
            "allowed": 50,
            "successRate": 95.0
        }
    }
}

class MockResponse:
    """Mock requests.Response for API testing"""
    
    def __init__(self, status_code: int, json_data: Any, content: Optional[bytes] = None):
        self.status_code = status_code
        self._json_data = json_data
        self.content = content or b''
        self.text = str(json_data)
    
    def json(self):
        return self._json_data
    
    def raise_for_status(self):
        if 400 <= self.status_code < 600:
            import requests
            raise requests.exceptions.HTTPError(f"HTTP Error: {self.status_code}")

class MockAsyncResponse:
    """Mock aiohttp.ClientResponse for async API testing"""
    
    def __init__(self, status: int, json_data: Any, text: Optional[str] = None):
        self.status = status
        self._json_data = json_data
        self._text = text or str(json_data)
    
    async def json(self):
        return self._json_data
    
    async def text(self):
        return self._text
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass
    
    def raise_for_status(self):
        if 400 <= self.status < 600:
            from aiohttp import ClientResponseError
            raise ClientResponseError(None, None, status=self.status, message=f"HTTP Error: {self.status}")

class MockAPI:
    """Mock Breaking Point API for testing"""
    
    def __init__(self, fail_mode: Optional[str] = None):
        self.fail_mode = fail_mode
        self.login_called = False
        self.logout_called = False
        self.get_tests_called = False
        self.run_test_called = False
        self.get_test_results_called = False
    
    def login(self):
        self.login_called = True
        if self.fail_mode == "login":
            raise AuthenticationError("Mock login failure")
        return True
    
    def logout(self):
        self.logout_called = True
        return True
    
    def get_tests(self):
        self.get_tests_called = True
        if self.fail_mode == "get_tests":
            raise APIError("Mock API error")
        return MOCK_TEST_LIST
    
    def run_test(self, test_id):
        self.run_test_called = True
        if self.fail_mode == "run_test":
            raise APIError("Mock API error")
        return {"runId": "run1"}
    
    def get_test_status(self, test_id, run_id):
        return "completed"
    
    def get_test_results(self, test_id, run_id, use_cache=True):
        self.get_test_results_called = True
        if self.fail_mode == "get_results":
            raise APIError("Mock API error")
        return MOCK_TEST_RESULT
    
    def __enter__(self):
        self.login()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.logout()

class MockAsyncAPI:
    """Mock Async Breaking Point API for testing"""
    
    def __init__(self, fail_mode: Optional[str] = None):
        self.fail_mode = fail_mode
        self.login_called = False
        self.logout_called = False
        self.get_tests_called = False
        self.run_test_called = False
        self.get_test_results_called = False
    
    async def login(self):
        self.login_called = True
        if self.fail_mode == "login":
            raise AuthenticationError("Mock login failure")
        return True
    
    async def logout(self):
        self.logout_called = True
        return True
    
    async def get_tests(self):
        self.get_tests_called = True
        if self.fail_mode == "get_tests":
            raise APIError("Mock API error")
        return MOCK_TEST_LIST
    
    async def run_test(self, test_id):
        self.run_test_called = True
        if self.fail_mode == "run_test":
            raise APIError("Mock API error")
        return {"runId": "run1"}
    
    async def get_test_status(self, test_id, run_id):
        return "completed"
    
    async def get_test_results(self, test_id, run_id, use_cache=True):
        self.get_test_results_called = True
        if self.fail_mode == "get_results":
            raise APIError("Mock API error")
        return MOCK_TEST_RESULT
    
    async def __aenter__(self):
        await self.login()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.logout()

class IntegrationTests(unittest.TestCase):
    """Integration tests for Breaking Point MCP Agent"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test environment"""
        # Initialize with test configuration
        initialize()
        
        # Set up test output directory
        cls.test_output_dir = os.path.join(os.path.dirname(__file__), "test_output")
        os.makedirs(cls.test_output_dir, exist_ok=True)
    
    def setUp(self):
        """Set up before each test"""
        # Create a clean output directory for each test
        self.test_name = self.id().split('.')[-1]
        self.test_dir = os.path.join(self.test_output_dir, self.test_name)
        os.makedirs(self.test_dir, exist_ok=True)
    
    def tearDown(self):
        """Clean up after each test"""
        pass
    
    @mock.patch.object(BreakingPointAPI, 'login')
    @mock.patch.object(BreakingPointAPI, 'logout')
    @mock.patch.object(BreakingPointAPI, 'get_tests')
    def test_api_connection(self, mock_get_tests, mock_logout, mock_login):
        """Test API connection with context manager"""
        # Set up mocks
        mock_login.return_value = True
        mock_logout.return_value = True
        mock_get_tests.return_value = MOCK_TEST_LIST
        
        # Test API with context manager
        with create_api() as api:
            # Check login was called
            self.assertTrue(mock_login.called, "API login method was not called")
            
            # Get tests
            tests = api.get_tests()
            self.assertEqual(len(tests), 3, "Should have returned 3 tests")
            self.assertEqual(tests[0]["id"], "test1", "First test ID should be 'test1'")
        
        # Check logout was called
        self.assertTrue(mock_logout.called, "API logout method was not called")
    
    @mock.patch.object(BreakingPointAPI, 'get_test_results')
    def test_analyzer_summary(self, mock_get_results):
        """Test analyzer summary generation"""
        # Set up mocks
        mock_get_results.return_value = MOCK_TEST_RESULT
        
        # Create API instance
        api = create_api()
        
        # Get test summary
        summary = get_test_result_summary(api, "test1", "run1")
        
        # Check summary
        self.assertEqual(summary["testId"], "test1", "Test ID should be 'test1'")
        self.assertEqual(summary["runId"], "run1", "Run ID should be 'run1'")
        self.assertEqual(summary["testName"], "Test 1", "Test name should be 'Test 1'")
        self.assertEqual(summary["testType"], "strike", "Test type should be 'strike'")
        
        # Check metrics
        self.assertIn("throughput", summary["metrics"], "Summary should include throughput metrics")
        self.assertIn("latency", summary["metrics"], "Summary should include latency metrics")
        self.assertIn("strikes", summary["metrics"], "Summary should include strikes metrics")
        
        # Check specific metrics
        self.assertEqual(summary["metrics"]["throughput"]["average"], 1250.5, "Throughput average should be 1250.5")
        self.assertEqual(summary["metrics"]["strikes"]["successRate"], 95.0, "Strike success rate should be 95.0")
    
    @mock.patch.object(BreakingPointAPI, 'get_test_results')
    def test_report_generation(self, mock_get_results):
        """Test report generation"""
        # Set up mocks
        mock_get_results.return_value = MOCK_TEST_RESULT
        
        # Create API instance
        api = create_api()
        
        # Generate report
        report_path = generate_report(
            api, "test1", "run1", 
            output_format="html", 
            report_type="standard",
            output_dir=self.test_dir
        )
        
        # Check report was created
        self.assertTrue(os.path.exists(report_path), f"Report file not created: {report_path}")
        self.assertTrue(os.path.getsize(report_path) > 0, "Report file is empty")
    
    @mock.patch.object(BreakingPointAPI, 'get_test_results')
    def test_chart_generation(self, mock_get_results):
        """Test chart generation"""
        # Set up mocks
        mock_get_results.return_value = MOCK_TEST_RESULT
        
        # Create API instance
        api = create_api()
        
        # Generate charts
        chart_paths = generate_charts(api, "test1", "run1", output_dir=self.test_dir)
        
        # Check charts were created
        self.assertTrue(len(chart_paths) > 0, "No charts were generated")
        for path in chart_paths:
            self.assertTrue(os.path.exists(path), f"Chart file not created: {path}")
            self.assertTrue(os.path.getsize(path) > 0, "Chart file is empty")
    
    def test_cache_operations(self):
        """Test cache operations"""
        # Get cache instance
        cache = get_cache()
        
        # Clear cache to start fresh
        cache.clear()
        
        # Test setting cache
        test_data = {"test": "data", "value": 123}
        result = cache.set("test_id", "run_id", test_data)
        self.assertTrue(result, "Cache set operation failed")
        
        # Test getting cache
        cached_data = cache.get("test_id", "run_id")
        self.assertIsNotNone(cached_data, "Cache get operation returned None")
        self.assertEqual(cached_data, test_data, "Cached data does not match original data")
        
        # Test invalidating cache
        result = cache.invalidate("test_id", "run_id")
        self.assertTrue(result, "Cache invalidate operation failed")
        
        # Verify cache was invalidated
        cached_data = cache.get("test_id", "run_id")
        self.assertIsNone(cached_data, "Cache was not properly invalidated")
    
    @mock.patch.object(BreakingPointAPI, 'login')
    @mock.patch.object(BreakingPointAPI, 'logout')
    @mock.patch.object(BreakingPointAPI, 'get_test_results')
    def test_error_handling(self, mock_get_results, mock_logout, mock_login):
        """Test error handling"""
        # Set up mocks
        mock_login.return_value = True
        mock_logout.return_value = True
        mock_get_results.side_effect = APIError("Test API error", status_code=500, endpoint="tests/test1/runs/run1/results")
        
        # Create API instance
        api = create_api()
        
        # Try to get test results, should raise APIError
        with self.assertRaises(APIError) as cm:
            api.get_test_results("test1", "run1")
        
        # Check error details
        error = cm.exception
        self.assertEqual(error.status_code, 500, "Error status code should be 500")
        self.assertEqual(error.endpoint, "tests/test1/runs/run1/results", "Error endpoint should be correct")
    
    @unittest.skipIf(sys.platform == "win32", "Async tests may be unstable on Windows")
    def test_async_api(self):
        """Test asynchronous API operations"""
        async def test_async():
            # Mock async session for API testing
            mock_api = MockAsyncAPI()
            
            # Test API with context manager
            async with mock_api as api:
                # Check login was called
                self.assertTrue(api.login_called, "API login method was not called")
                
                # Get tests
                tests = await api.get_tests()
                self.assertEqual(len(tests), 3, "Should have returned 3 tests")
                
                # Run a test
                result = await api.run_test("test1")
                self.assertEqual(result["runId"], "run1", "Run ID should be 'run1'")
                
                # Get test results
                results = await api.get_test_results("test1", "run1")
                self.assertEqual(results["testId"], "test1", "Test ID should be 'test1'")
            
            # Check logout was called
            self.assertTrue(mock_api.logout_called, "API logout method was not called")
            
            return True
        
        # Run async test
        loop = asyncio.get_event_loop()
        result = loop.run_until_complete(test_async())
        self.assertTrue(result, "Async API test failed")
    
    @unittest.skipIf(sys.platform == "win32", "Async tests may be unstable on Windows")
    def test_async_analyzer(self):
        """Test asynchronous analyzer operations"""
        async def test_async():
            # Mock async API
            mock_api = MockAsyncAPI()
            
            # Get test summary
            summary = await async_get_test_result_summary(mock_api, "test1", "run1")
            
            # Check summary
            self.assertEqual(summary["testId"], "test1", "Test ID should be 'test1'")
            self.assertEqual(summary["testType"], "strike", "Test type should be 'strike'")
            
            # Check metrics
            self.assertIn("throughput", summary["metrics"], "Summary should include throughput metrics")
            self.assertIn("strikes", summary["metrics"], "Summary should include strikes metrics")
            
            return True
        
        # Run async test
        loop = asyncio.get_event_loop()
        result = loop.run_until_complete(test_async())
        self.assertTrue(result, "Async analyzer test failed")
    
    def test_plugin_system(self):
        """Test plugin system"""
        # Import plugin registry
        from src.analyzer.plugins.registry import get_plugin_manager
        
        # Get plugin manager
        manager = get_plugin_manager()
        
        # Check built-in plugins
        self.assertTrue(len(manager.report_generators) > 0, "No report generators found")
        self.assertTrue(len(manager.chart_generators) > 0, "No chart generators found")
        
        # Check specific report types
        self.assertIn("standard", manager.report_generators, "Standard report generator missing")
        self.assertIn("executive", manager.report_generators, "Executive report generator missing")
        self.assertIn("detailed", manager.report_generators, "Detailed report generator missing")
        
        # Check specific chart types
        self.assertIn("throughput", manager.chart_generators, "Throughput chart generator missing")
        self.assertIn("latency", manager.chart_generators, "Latency chart generator missing")
    
    def test_config_system(self):
        """Test configuration system"""
        # Get configuration
        config = get_config()
        
        # Test getting values
        api_config = config.get_api_config()
        self.assertIsNotNone(api_config, "API configuration is None")
        self.assertIn("host", api_config, "API configuration missing 'host'")
        
        # Test setting and getting values
        config.set("test", "key", "value")
        value = config.get("test", "key")
        self.assertEqual(value, "value", "Configuration value not set correctly")
        
        # Test environment variables
        original_env = os.environ.copy()
        
        try:
            os.environ["BP_AGENT_TEST_KEY"] = "env_value"
            config.load_from_env()
            value = config.get("test", "key")
            self.assertEqual(value, "env_value", "Environment variable not loaded correctly")
        finally:
            # Restore original environment
            os.environ.clear()
            os.environ.update(original_env)

def main():
    """Run integration tests"""
    parser = argparse.ArgumentParser(description="Run Breaking Point MCP Agent integration tests")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--test", "-t", help="Run specific test")
    args = parser.parse_args()
    
    # Configure test verbosity
    verbosity = 2 if args.verbose else 1
    
    # Run tests
    if args.test:
        suite = unittest.TestSuite()
        suite.addTest(IntegrationTests(args.test))
        unittest.TextTestRunner(verbosity=verbosity).run(suite)
    else:
        unittest.main(argv=[sys.argv[0]], verbosity=verbosity)

if __name__ == "__main__":
    main()
