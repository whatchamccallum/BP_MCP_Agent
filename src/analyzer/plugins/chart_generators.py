"""
Chart generator plugins for Breaking Point test results.
"""
import os
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple, cast

from .base import ChartGenerator, TestSummary

class ThroughputChartGenerator(ChartGenerator):
    """Generates throughput charts for test results"""
    
    def generate(self, summary: TestSummary, raw_results: Dict[str, Any], 
                output_file: str) -> str:
        """Generate a throughput chart
        
        Args:
            summary: Test summary data
            raw_results: Raw test results
            output_file: Path to output file
            
        Returns:
            str: Path to generated chart
        """
        # Check if time series data is available
        if "timeSeriesData" not in raw_results:
            # Fall back to simple bar chart with average and maximum
            return self._generate_summary_chart(summary, output_file)
        
        # Extract time series data
        time_series = raw_results["timeSeriesData"]
        
        # Extract timestamps and throughput values
        timestamps = []
        throughput_values = []
        
        for point in time_series:
            if "timestamp" in point and "throughput" in point:
                # Parse timestamp
                try:
                    ts = datetime.fromisoformat(point["timestamp"].replace('Z', '+00:00'))
                    timestamps.append(ts)
                    throughput_values.append(float(point["throughput"]))
                except (ValueError, TypeError):
                    # Skip invalid data points
                    continue
        
        if not timestamps or not throughput_values:
            # Fall back to summary chart if no valid time series data
            return self._generate_summary_chart(summary, output_file)
        
        # Create figure
        plt.figure(figsize=(12, 6))
        
        # Plot throughput over time
        plt.plot(timestamps, throughput_values, '-', linewidth=2, color='#0066cc')
        
        # Add average line
        avg_throughput = summary["metrics"].get("throughput", {}).get("average", 0)
        if avg_throughput > 0:
            plt.axhline(y=avg_throughput, color='r', linestyle='--', label=f'Average: {avg_throughput} Mbps')
        
        # Format the chart
        plt.title(f'Throughput Over Time: {summary["testName"]}')
        plt.xlabel('Time')
        plt.ylabel('Throughput (Mbps)')
        plt.grid(True, linestyle='--', alpha=0.7)
        
        # Format x-axis with dates
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
        plt.gca().xaxis.set_major_locator(mdates.AutoDateLocator())
        
        # Add legend
        plt.legend()
        
        # Adjust layout
        plt.tight_layout()
        
        # Save the chart
        plt.savefig(output_file, dpi=300)
        plt.close()
        
        return output_file
    
    def _generate_summary_chart(self, summary: TestSummary, output_file: str) -> str:
        """Generate a summary bar chart for throughput
        
        Args:
            summary: Test summary data
            output_file: Path to output file
            
        Returns:
            str: Path to generated chart
        """
        # Get throughput metrics
        if "throughput" not in summary["metrics"]:
            # Cannot generate chart without throughput data
            raise ValueError("No throughput data available for chart generation")
        
        throughput = summary["metrics"]["throughput"]
        avg_throughput = throughput.get("average", 0)
        max_throughput = throughput.get("maximum", 0)
        
        # Create figure
        plt.figure(figsize=(8, 6))
        
        # Create bar chart
        metrics = ['Average', 'Maximum']
        values = [avg_throughput, max_throughput]
        
        plt.bar(metrics, values, color=['#0066cc', '#66aaff'])
        
        # Add labels
        for i, v in enumerate(values):
            plt.text(i, v + 0.1, f"{v:.2f}", ha='center')
        
        # Format the chart
        plt.title(f'Throughput Metrics: {summary["testName"]}')
        plt.ylabel('Throughput (Mbps)')
        plt.grid(True, axis='y', linestyle='--', alpha=0.7)
        
        # Adjust layout
        plt.tight_layout()
        
        # Save the chart
        plt.savefig(output_file, dpi=300)
        plt.close()
        
        return output_file

class LatencyChartGenerator(ChartGenerator):
    """Generates latency charts for test results"""
    
    def generate(self, summary: TestSummary, raw_results: Dict[str, Any], 
                output_file: str) -> str:
        """Generate a latency chart
        
        Args:
            summary: Test summary data
            raw_results: Raw test results
            output_file: Path to output file
            
        Returns:
            str: Path to generated chart
        """
        # Check if time series data is available
        if "timeSeriesData" not in raw_results:
            # Fall back to simple bar chart with average and maximum
            return self._generate_summary_chart(summary, output_file)
        
        # Extract time series data
        time_series = raw_results["timeSeriesData"]
        
        # Extract timestamps and latency values
        timestamps = []
        latency_values = []
        
        for point in time_series:
            if "timestamp" in point and "latency" in point:
                # Parse timestamp
                try:
                    ts = datetime.fromisoformat(point["timestamp"].replace('Z', '+00:00'))
                    timestamps.append(ts)
                    latency_values.append(float(point["latency"]))
                except (ValueError, TypeError):
                    # Skip invalid data points
                    continue
        
        if not timestamps or not latency_values:
            # Fall back to summary chart if no valid time series data
            return self._generate_summary_chart(summary, output_file)
        
        # Create figure
        plt.figure(figsize=(12, 6))
        
        # Plot latency over time
        plt.plot(timestamps, latency_values, '-', linewidth=2, color='#cc6600')
        
        # Add average line
        avg_latency = summary["metrics"].get("latency", {}).get("average", 0)
        if avg_latency > 0:
            plt.axhline(y=avg_latency, color='r', linestyle='--', label=f'Average: {avg_latency} ms')
        
        # Format the chart
        plt.title(f'Latency Over Time: {summary["testName"]}')
        plt.xlabel('Time')
        plt.ylabel('Latency (ms)')
        plt.grid(True, linestyle='--', alpha=0.7)
        
        # Format x-axis with dates
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
        plt.gca().xaxis.set_major_locator(mdates.AutoDateLocator())
        
        # Add legend
        plt.legend()
        
        # Adjust layout
        plt.tight_layout()
        
        # Save the chart
        plt.savefig(output_file, dpi=300)
        plt.close()
        
        return output_file
    
    def _generate_summary_chart(self, summary: TestSummary, output_file: str) -> str:
        """Generate a summary bar chart for latency
        
        Args:
            summary: Test summary data
            output_file: Path to output file
            
        Returns:
            str: Path to generated chart
        """
        # Get latency metrics
        if "latency" not in summary["metrics"]:
            # Cannot generate chart without latency data
            raise ValueError("No latency data available for chart generation")
        
        latency = summary["metrics"]["latency"]
        avg_latency = latency.get("average", 0)
        max_latency = latency.get("maximum", 0)
        
        # Create figure
        plt.figure(figsize=(8, 6))
        
        # Create bar chart
        metrics = ['Average', 'Maximum']
        values = [avg_latency, max_latency]
        
        plt.bar(metrics, values, color=['#cc6600', '#ff9933'])
        
        # Add labels
        for i, v in enumerate(values):
            plt.text(i, v + 0.1, f"{v:.2f}", ha='center')
        
        # Format the chart
        plt.title(f'Latency Metrics: {summary["testName"]}')
        plt.ylabel('Latency (ms)')
        plt.grid(True, axis='y', linestyle='--', alpha=0.7)
        
        # Adjust layout
        plt.tight_layout()
        
        # Save the chart
        plt.savefig(output_file, dpi=300)
        plt.close()
        
        return output_file

class StrikeChartGenerator(ChartGenerator):
    """Generates security strike charts for test results"""
    
    def generate(self, summary: TestSummary, raw_results: Dict[str, Any], 
                output_file: str) -> str:
        """Generate a strike results chart
        
        Args:
            summary: Test summary data
            raw_results: Raw test results
            output_file: Path to output file
            
        Returns:
            str: Path to generated chart
        """
        # Check if strikes data is available
        if "strikes" not in summary["metrics"]:
            raise ValueError("No strikes data available for chart generation")
        
        strikes = summary["metrics"]["strikes"]
        
        # Get strike counts
        blocked = strikes.get("blocked", 0)
        allowed = strikes.get("allowed", 0)
        
        # Create figure
        plt.figure(figsize=(10, 6))
        
        # Create pie chart
        labels = ['Blocked', 'Allowed']
        sizes = [blocked, allowed]
        colors = ['#4CAF50', '#F44336']
        explode = (0.1, 0)  # explode the first slice (Blocked)
        
        # Plot pie chart
        plt.pie(sizes, explode=explode, labels=labels, colors=colors,
                autopct='%1.1f%%', shadow=True, startangle=140)
        plt.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle
        
        # Add title
        plt.title(f'Strike Test Results: {summary["testName"]}')
        
        # Add legend with counts
        plt.legend([f'Blocked: {blocked}', f'Allowed: {allowed}'], loc='lower left')
        
        # Adjust layout
        plt.tight_layout()
        
        # Save the chart
        plt.savefig(output_file, dpi=300)
        plt.close()
        
        # If detailed strike category data is available, create a second chart
        if "strikeCategories" in raw_results and len(raw_results["strikeCategories"]) > 0:
            # Create a second chart for strike categories
            category_file = os.path.splitext(output_file)[0] + "_categories" + os.path.splitext(output_file)[1]
            self._generate_category_chart(raw_results["strikeCategories"], category_file)
            
        return output_file
    
    def _generate_category_chart(self, categories: Dict[str, Dict[str, int]], output_file: str) -> str:
        """Generate a chart showing strikes by category
        
        Args:
            categories: Dictionary of strike categories
            output_file: Path to output file
            
        Returns:
            str: Path to generated chart
        """
        # Extract category names and counts
        cat_names = []
        blocked_counts = []
        allowed_counts = []
        
        for cat_name, cat_data in categories.items():
            cat_names.append(cat_name)
            blocked_counts.append(cat_data.get("blocked", 0))
            allowed_counts.append(cat_data.get("allowed", 0))
        
        # Create figure
        plt.figure(figsize=(12, 6))
        
        # Create stacked bar chart
        x = range(len(cat_names))
        width = 0.35
        
        plt.bar(x, blocked_counts, width, label='Blocked', color='#4CAF50')
        plt.bar(x, allowed_counts, width, bottom=blocked_counts, label='Allowed', color='#F44336')
        
        # Add labels and title
        plt.xlabel('Strike Categories')
        plt.ylabel('Count')
        plt.title('Strikes by Category')
        plt.xticks(x, cat_names, rotation=45, ha='right')
        plt.legend()
        
        # Adjust layout
        plt.tight_layout()
        
        # Save the chart
        plt.savefig(output_file, dpi=300)
        plt.close()
        
        return output_file

class TransactionChartGenerator(ChartGenerator):
    """Generates transaction charts for test results"""
    
    def generate(self, summary: TestSummary, raw_results: Dict[str, Any], 
                output_file: str) -> str:
        """Generate a transaction results chart
        
        Args:
            summary: Test summary data
            raw_results: Raw test results
            output_file: Path to output file
            
        Returns:
            str: Path to generated chart
        """
        # Check if transactions data is available
        if "transactions" not in summary["metrics"]:
            raise ValueError("No transactions data available for chart generation")
        
        transactions = summary["metrics"]["transactions"]
        
        # Get transaction counts
        successful = transactions.get("successful", 0)
        failed = transactions.get("failed", 0)
        
        # Create figure
        plt.figure(figsize=(10, 6))
        
        # Create pie chart
        labels = ['Successful', 'Failed']
        sizes = [successful, failed]
        colors = ['#4CAF50', '#F44336']
        explode = (0.1, 0)  # explode the first slice (Successful)
        
        # Plot pie chart
        plt.pie(sizes, explode=explode, labels=labels, colors=colors,
                autopct='%1.1f%%', shadow=True, startangle=140)
        plt.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle
        
        # Add title
        plt.title(f'Transaction Test Results: {summary["testName"]}')
        
        # Add legend with counts
        plt.legend([f'Successful: {successful}', f'Failed: {failed}'], loc='lower left')
        
        # Adjust layout
        plt.tight_layout()
        
        # Save the chart
        plt.savefig(output_file, dpi=300)
        plt.close()
        
        # If detailed transaction type data is available, create a second chart
        if "transactionResults" in raw_results and len(raw_results["transactionResults"]) > 0:
            # Create a second chart for transaction types
            type_file = os.path.splitext(output_file)[0] + "_types" + os.path.splitext(output_file)[1]
            self._generate_type_chart(raw_results["transactionResults"], type_file)
            
        return output_file
    
    def _generate_type_chart(self, types: Dict[str, Dict[str, int]], output_file: str) -> str:
        """Generate a chart showing transactions by type
        
        Args:
            types: Dictionary of transaction types
            output_file: Path to output file
            
        Returns:
            str: Path to generated chart
        """
        # Extract type names and counts
        type_names = []
        successful_counts = []
        failed_counts = []
        
        for type_name, type_data in types.items():
            type_names.append(type_name)
            successful_counts.append(type_data.get("successful", 0))
            failed_counts.append(type_data.get("failed", 0))
        
        # Create figure
        plt.figure(figsize=(12, 6))
        
        # Create stacked bar chart
        x = range(len(type_names))
        width = 0.35
        
        plt.bar(x, successful_counts, width, label='Successful', color='#4CAF50')
        plt.bar(x, failed_counts, width, bottom=successful_counts, label='Failed', color='#F44336')
        
        # Add labels and title
        plt.xlabel('Transaction Types')
        plt.ylabel('Count')
        plt.title('Transactions by Type')
        plt.xticks(x, type_names, rotation=45, ha='right')
        plt.legend()
        
        # Adjust layout
        plt.tight_layout()
        
        # Save the chart
        plt.savefig(output_file, dpi=300)
        plt.close()
        
        return output_file

class ComparisonChartGenerator(ChartGenerator):
    """Generates comparison charts for multiple test results"""
    
    def generate(self, summary1: TestSummary, summary2: TestSummary, metric: str, 
                output_file: str) -> str:
        """Generate a comparison chart for two test runs
        
        Args:
            summary1: First test summary data
            summary2: Second test summary data
            metric: Metric to compare (throughput, latency, strikes, transactions)
            output_file: Path to output file
            
        Returns:
            str: Path to generated chart
        """
        # Validate metric type
        if metric not in ["throughput", "latency", "strikes", "transactions"]:
            raise ValueError(f"Unsupported metric for comparison: {metric}")
        
        # Check if both summaries have the requested metric
        if metric not in summary1["metrics"] or metric not in summary2["metrics"]:
            raise ValueError(f"One or both test summaries are missing {metric} metrics")
        
        # Get test names
        test1_name = summary1["testName"]
        test2_name = summary2["testName"]
        
        # Create figure
        plt.figure(figsize=(12, 6))
        
        if metric in ["throughput", "latency"]:
            # Performance metric comparison (bar chart)
            return self._generate_performance_comparison(
                summary1, summary2, metric, test1_name, test2_name, output_file
            )
        elif metric == "strikes":
            # Strike metric comparison (bar chart)
            return self._generate_strike_comparison(
                summary1, summary2, test1_name, test2_name, output_file
            )
        elif metric == "transactions":
            # Transaction metric comparison (bar chart)
            return self._generate_transaction_comparison(
                summary1, summary2, test1_name, test2_name, output_file
            )
    
    def _generate_performance_comparison(self, summary1: TestSummary, summary2: TestSummary, 
                                        metric: str, test1_name: str, test2_name: str,
                                        output_file: str) -> str:
        """Generate a performance metric comparison chart
        
        Args:
            summary1: First test summary data
            summary2: Second test summary data
            metric: Metric to compare (throughput or latency)
            test1_name: Name of first test
            test2_name: Name of second test
            output_file: Path to output file
            
        Returns:
            str: Path to generated chart
        """
        # Get metric data
        metric1 = summary1["metrics"][metric]
        metric2 = summary2["metrics"][metric]
        
        # Get values for comparison
        avg1 = metric1.get("average", 0)
        max1 = metric1.get("maximum", 0)
        avg2 = metric2.get("average", 0)
        max2 = metric2.get("maximum", 0)
        
        # Get unit
        unit = metric1.get("unit", "")
        
        # Create figure
        plt.figure(figsize=(10, 6))
        
        # Set up bar positions
        x = [0, 1]  # positions for average and maximum
        width = 0.35  # width of the bars
        
        # Create bars
        plt.bar([pos - width/2 for pos in x], [avg1, max1], width, label=test1_name, color='#0066cc')
        plt.bar([pos + width/2 for pos in x], [avg2, max2], width, label=test2_name, color='#cc6600')
        
        # Add labels
        plt.title(f'{metric.capitalize()} Comparison')
        plt.ylabel(f'{metric.capitalize()} ({unit})')
        plt.xticks(x, ['Average', 'Maximum'])
        
        # Calculate improvement percentages
        avg_diff_pct = ((avg2 - avg1) / avg1 * 100) if avg1 > 0 else 0
        max_diff_pct = ((max2 - max1) / max1 * 100) if max1 > 0 else 0
        
        # Add value labels to bars
        plt.text(x[0] - width/2, avg1 + 0.1, f"{avg1:.2f}", ha='center')
        plt.text(x[1] - width/2, max1 + 0.1, f"{max1:.2f}", ha='center')
        plt.text(x[0] + width/2, avg2 + 0.1, f"{avg2:.2f}", ha='center')
        plt.text(x[1] + width/2, max2 + 0.1, f"{max2:.2f}", ha='center')
        
        # Add a table with comparison data
        table_data = [
            ['Metric', test1_name, test2_name, 'Difference', 'Change'],
            ['Average', f"{avg1:.2f} {unit}", f"{avg2:.2f} {unit}", 
             f"{avg2-avg1:.2f} {unit}", f"{avg_diff_pct:.1f}%"],
            ['Maximum', f"{max1:.2f} {unit}", f"{max2:.2f} {unit}", 
             f"{max2-max1:.2f} {unit}", f"{max_diff_pct:.1f}%"]
        ]
        
        # Add table below the chart
        plt.table(cellText=table_data[1:], colLabels=table_data[0], 
                 loc='bottom', cellLoc='center', bbox=[0, -0.3, 1, 0.2])
        
        # Adjust layout
        plt.subplots_adjust(bottom=0.25)
        
        # Add legend
        plt.legend()
        
        # Add grid
        plt.grid(True, axis='y', linestyle='--', alpha=0.7)
        
        # Save the chart
        plt.savefig(output_file, dpi=300)
        plt.close()
        
        return output_file
    
    def _generate_strike_comparison(self, summary1: TestSummary, summary2: TestSummary,
                                   test1_name: str, test2_name: str, output_file: str) -> str:
        """Generate a strike metric comparison chart
        
        Args:
            summary1: First test summary data
            summary2: Second test summary data
            test1_name: Name of first test
            test2_name: Name of second test
            output_file: Path to output file
            
        Returns:
            str: Path to generated chart
        """
        # Get strike data
        strikes1 = summary1["metrics"]["strikes"]
        strikes2 = summary2["metrics"]["strikes"]
        
        # Get values for comparison
        attempted1 = strikes1.get("attempted", 0)
        blocked1 = strikes1.get("blocked", 0)
        allowed1 = strikes1.get("allowed", 0)
        rate1 = strikes1.get("successRate", 0)
        
        attempted2 = strikes2.get("attempted", 0)
        blocked2 = strikes2.get("blocked", 0)
        allowed2 = strikes2.get("allowed", 0)
        rate2 = strikes2.get("successRate", 0)
        
        # Create figure
        plt.figure(figsize=(12, 8))
        
        # Create subplot for counts
        plt.subplot(2, 1, 1)
        
        # Set up bar positions
        x = [0, 1, 2]  # positions for attempted, blocked, allowed
        width = 0.35  # width of the bars
        
        # Create bars for counts
        plt.bar([pos - width/2 for pos in x], [attempted1, blocked1, allowed1], width, label=test1_name, color='#0066cc')
        plt.bar([pos + width/2 for pos in x], [attempted2, blocked2, allowed2], width, label=test2_name, color='#cc6600')
        
        # Add labels
        plt.title('Strike Test Comparison - Counts')
        plt.ylabel('Count')
        plt.xticks(x, ['Attempted', 'Blocked', 'Allowed'])
        
        # Add value labels to bars
        for i, v in enumerate([attempted1, blocked1, allowed1]):
            plt.text(x[i] - width/2, v + 0.1, str(v), ha='center')
        
        for i, v in enumerate([attempted2, blocked2, allowed2]):
            plt.text(x[i] + width/2, v + 0.1, str(v), ha='center')
        
        # Add legend
        plt.legend()
        
        # Add grid
        plt.grid(True, axis='y', linestyle='--', alpha=0.7)
        
        # Create subplot for success rates
        plt.subplot(2, 1, 2)
        
        # Create bars for success rates
        x = [0]  # position for success rate
        plt.bar([pos - width/2 for pos in x], [rate1], width, label=test1_name, color='#0066cc')
        plt.bar([pos + width/2 for pos in x], [rate2], width, label=test2_name, color='#cc6600')
        
        # Add labels
        plt.title('Strike Test Comparison - Success Rate')
        plt.ylabel('Success Rate (%)')
        plt.xticks(x, ['Success Rate'])
        
        # Add value labels to bars
        plt.text(x[0] - width/2, rate1 + 0.1, f"{rate1:.1f}%", ha='center')
        plt.text(x[0] + width/2, rate2 + 0.1, f"{rate2:.1f}%", ha='center')
        
        # Add improvement percentage
        rate_diff_pct = ((rate2 - rate1) / rate1 * 100) if rate1 > 0 else 0
        plt.figtext(0.5, 0.25, f"Success Rate Change: {rate2 - rate1:.1f}% ({rate_diff_pct:.1f}% relative change)",
                   ha='center', bbox={"facecolor":"lightgray", "alpha":0.5, "pad":5})
        
        # Add grid
        plt.grid(True, axis='y', linestyle='--', alpha=0.7)
        
        # Adjust layout
        plt.tight_layout()
        
        # Save the chart
        plt.savefig(output_file, dpi=300)
        plt.close()
        
        return output_file
    
    def _generate_transaction_comparison(self, summary1: TestSummary, summary2: TestSummary,
                                        test1_name: str, test2_name: str, output_file: str) -> str:
        """Generate a transaction metric comparison chart
        
        Args:
            summary1: First test summary data
            summary2: Second test summary data
            test1_name: Name of first test
            test2_name: Name of second test
            output_file: Path to output file
            
        Returns:
            str: Path to generated chart
        """
        # Get transaction data
        tx1 = summary1["metrics"]["transactions"]
        tx2 = summary2["metrics"]["transactions"]
        
        # Get values for comparison
        attempted1 = tx1.get("attempted", 0)
        successful1 = tx1.get("successful", 0)
        failed1 = tx1.get("failed", 0)
        rate1 = tx1.get("successRate", 0)
        
        attempted2 = tx2.get("attempted", 0)
        successful2 = tx2.get("successful", 0)
        failed2 = tx2.get("failed", 0)
        rate2 = tx2.get("successRate", 0)
        
        # Create figure
        plt.figure(figsize=(12, 8))
        
        # Create subplot for counts
        plt.subplot(2, 1, 1)
        
        # Set up bar positions
        x = [0, 1, 2]  # positions for attempted, successful, failed
        width = 0.35  # width of the bars
        
        # Create bars for counts
        plt.bar([pos - width/2 for pos in x], [attempted1, successful1, failed1], width, label=test1_name, color='#0066cc')
        plt.bar([pos + width/2 for pos in x], [attempted2, successful2, failed2], width, label=test2_name, color='#cc6600')
        
        # Add labels
        plt.title('Transaction Test Comparison - Counts')
        plt.ylabel('Count')
        plt.xticks(x, ['Attempted', 'Successful', 'Failed'])
        
        # Add value labels to bars
        for i, v in enumerate([attempted1, successful1, failed1]):
            plt.text(x[i] - width/2, v + 0.1, str(v), ha='center')
        
        for i, v in enumerate([attempted2, successful2, failed2]):
            plt.text(x[i] + width/2, v + 0.1, str(v), ha='center')
        
        # Add legend
        plt.legend()
        
        # Add grid
        plt.grid(True, axis='y', linestyle='--', alpha=0.7)
        
        # Create subplot for success rates
        plt.subplot(2, 1, 2)
        
        # Create bars for success rates
        x = [0]  # position for success rate
        plt.bar([pos - width/2 for pos in x], [rate1], width, label=test1_name, color='#0066cc')
        plt.bar([pos + width/2 for pos in x], [rate2], width, label=test2_name, color='#cc6600')
        
        # Add labels
        plt.title('Transaction Test Comparison - Success Rate')
        plt.ylabel('Success Rate (%)')
        plt.xticks(x, ['Success Rate'])
        
        # Add value labels to bars
        plt.text(x[0] - width/2, rate1 + 0.1, f"{rate1:.1f}%", ha='center')
        plt.text(x[0] + width/2, rate2 + 0.1, f"{rate2:.1f}%", ha='center')
        
        # Add improvement percentage
        rate_diff_pct = ((rate2 - rate1) / rate1 * 100) if rate1 > 0 else 0
        plt.figtext(0.5, 0.25, f"Success Rate Change: {rate2 - rate1:.1f}% ({rate_diff_pct:.1f}% relative change)",
                   ha='center', bbox={"facecolor":"lightgray", "alpha":0.5, "pad":5})
        
        # Add grid
        plt.grid(True, axis='y', linestyle='--', alpha=0.7)
        
        # Adjust layout
        plt.tight_layout()
        
        # Save the chart
        plt.savefig(output_file, dpi=300)
        plt.close()
        
        return output_file
