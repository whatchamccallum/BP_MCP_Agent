"""
Test cases for the Breaking Point Analyzer
"""

import unittest
import os
from unittest.mock import MagicMock, patch
from src.api import BreakingPointAPI
from src.analyzer import (
    create_analyzer,
    get_test_result_summary,
    compare_test_results,
    generate_report,
    generate_charts,
    compare_charts,
    batch_process_tests
)

class TestAnalyzer(unittest.TestCase):
    """Test cases for the Breaking Point Analyzer"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Create a mock BP API instance
        self.bp_api = MagicMock(spec=BreakingPointAPI)
        
        # Mock test result data
        self.mock_test_result = {
            "testName": "Test 1",
            "testType": "strike",
            "startTime": "2023-01-01T10:00:00",
            "endTime": "2023-01-01T10:30:00",
            "duration": 1800,
            "status": "completed",
            "metrics": {
                "throughput": {
                    "average": 1000,
                    "maximum": 1500
                },
                "latency": {
                    "average": 10,
                    "maximum": 50
                },
                "strikes": {
                    "attempted": 100,
                    "blocked": 90,
                    "allowed": 10,
                    "successRate": 90
                }
            },
            "timeseries": {
                "throughput": {
                    "timestamps": [0, 60, 120, 180],
                    "values": [500, 800, 1000, 1200]
                },
                "latency": {
                    "timestamps": [0, 60, 120, 180],
                    "values": [5, 8, 10, 12]
                }
            }
        }
        
        # Configure the mock to return our test data
        self.bp_api.get_test_results.return_value = self.mock_test_result
        
        # Create output directories for tests
        os.makedirs("./test_output", exist_ok=True)

    def tearDown(self):
        """Tear down test fixtures"""
        # Clean up any files created during tests
        for file in os.listdir("./test_output"):
            try:
                os.remove(os.path.join("./test_output", file))
            except:
                pass
    
    def test_create_analyzer(self):
        """Test creating an analyzer instance"""
        analyzer = create_analyzer(self.bp_api)
        self.assertIsNotNone(analyzer)
    
    def test_get_test_result_summary(self):
        """Test getting a test result summary"""
        summary = get_test_result_summary(self.bp_api, "test1", "run1")
        
        # Verify the BP API was called correctly
        self.bp_api.get_test_results.assert_called_once_with("test1", "run1")
        
        # Verify the summary contains the expected data
        self.assertEqual(summary["testName"], "Test 1")
        self.assertEqual(summary["testType"], "strike")
        self.assertEqual(summary["status"], "completed")
        self.assertIn("throughput", summary["metrics"])
        self.assertIn("latency", summary["metrics"])
        self.assertIn("strikes", summary["metrics"])
    
    def test_compare_test_results(self):
        """Test comparing test results"""
        # Configure the mock to return different data for the second test
        mock_test_result2 = self.mock_test_result.copy()
        mock_test_result2["testName"] = "Test 2"
        mock_test_result2["metrics"]["throughput"]["average"] = 1200
        
        # Use side_effect to return different values on successive calls
        self.bp_api.get_test_results.side_effect = [self.mock_test_result, mock_test_result2]
        
        comparison = compare_test_results(self.bp_api, "test1", "run1", "test2", "run2")
        
        # Verify the BP API was called correctly
        self.assertEqual(self.bp_api.get_test_results.call_count, 2)
        
        # Verify the comparison contains the expected data
        self.assertIn("test1", comparison)
        self.assertIn("test2", comparison)
        self.assertIn("metrics", comparison)
        self.assertIn("throughput", comparison["metrics"])
        
        # Verify the comparison calculations are correct
        self.assertEqual(comparison["metrics"]["throughput"]["difference"]["average"], 200)
        self.assertEqual(comparison["metrics"]["throughput"]["difference"]["percentage"], 20)
    
    def test_generate_report(self):
        """Test generating a report"""
        # Patch the open function to avoid actually writing files
        with patch("builtins.open", unittest.mock.mock_open()) as mock_file:
            report_path = generate_report(self.bp_api, "test1", "run1", "html", "standard", "./test_output")
            
            # Verify the BP API was called correctly
            self.bp_api.get_test_results.assert_called_once_with("test1", "run1")
            
            # Verify the file was opened for writing
            mock_file.assert_called()
            
            # Verify the report path is as expected
            self.assertTrue(report_path.endswith(".html"))
            self.assertTrue("test1" in report_path)
            self.assertTrue("run1" in report_path)
    
    @patch("matplotlib.pyplot.savefig")  # Mock matplotlib to avoid actually creating images
    def test_generate_charts(self, mock_savefig):
        """Test generating charts"""
        chart_paths = generate_charts(self.bp_api, "test1", "run1", "./test_output")
        
        # Verify the BP API was called correctly
        self.bp_api.get_test_results.assert_called_once_with("test1", "run1")
        
        # Since we have throughput and latency timeseries data, and strikes metrics,
        # we should have gotten at least 3 charts
        self.assertGreaterEqual(len(chart_paths), 3)
        
        # Verify matplotlib was used to save figures
        self.assertGreaterEqual(mock_savefig.call_count, 3)
    
    @patch("matplotlib.pyplot.savefig")  # Mock matplotlib to avoid actually creating images
    def test_compare_charts(self, mock_savefig):
        """Test comparing charts"""
        # Configure the mock to return different data for the second test
        mock_test_result2 = self.mock_test_result.copy()
        mock_test_result2["testName"] = "Test 2"
        
        # Use side_effect to return different values on successive calls
        self.bp_api.get_test_results.side_effect = [self.mock_test_result, mock_test_result2]
        
        chart_path = compare_charts(self.bp_api, "test1", "run1", "test2", "run2", "throughput", "./test_output")
        
        # Verify the BP API was called correctly
        self.assertEqual(self.bp_api.get_test_results.call_count, 2)
        
        # Verify we got a chart path back
        self.assertIsNotNone(chart_path)
        self.assertTrue(chart_path.endswith(".png"))
        
        # Verify matplotlib was used to save a figure
        mock_savefig.assert_called_once()
    
    def test_batch_process_tests(self):
        """Test batch processing multiple tests"""
        # Configure the mock to return the same data for all tests
        self.bp_api.get_test_results.return_value = self.mock_test_result
        
        # Patch the necessary functions to avoid actually creating files
        with patch("src.analyzer.generate_report") as mock_generate_report, \
             patch("src.analyzer.generate_charts") as mock_generate_charts:
            
            # Set up the mocks to return something
            mock_generate_report.return_value = "report.html"
            mock_generate_charts.return_value = ["chart1.png", "chart2.png"]
            
            test_runs = [("test1", "run1"), ("test2", "run2")]
            results = batch_process_tests(self.bp_api, test_runs, "./test_output")
            
            # Verify the batch process called the API for each test
            self.assertEqual(self.bp_api.get_test_results.call_count, 2)
            
            # Verify we got a result for each test
            self.assertEqual(len(results), 2)
            
            # Verify the report and charts were generated for each test
            self.assertEqual(mock_generate_report.call_count, 2)
            self.assertEqual(mock_generate_charts.call_count, 2)

if __name__ == "__main__":
    unittest.main()
