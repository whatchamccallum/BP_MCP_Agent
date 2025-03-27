"""
Chart generation module for test result visualization
"""

import os
import matplotlib.pyplot as plt
from typing import Dict, List, Any

def generate_charts(bp_api, test_id: str, run_id: str, output_dir: str = "./") -> List[str]:
    """Generate charts for test results
    
    Args:
        bp_api: Breaking Point API instance
        test_id: Test ID
        run_id: Run ID
        output_dir: Output directory
        
    Returns:
        List[str]: Paths to generated chart files
    """
    results = bp_api.get_test_results(test_id, run_id)
    chart_files = []
    
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Extract time series data if available
    timeseries = results.get("timeseries", {})
    if "throughput" in timeseries:
        # Plot throughput over time
        plt.figure(figsize=(10, 6))
        plt.plot(timeseries["throughput"]["timestamps"], timeseries["throughput"]["values"])
        plt.title(f"Throughput over Time - {results.get('testName', 'Unknown Test')}")
        plt.xlabel("Time (seconds)")
        plt.ylabel("Throughput (Mbps)")
        plt.grid(True)
        
        filename = os.path.join(output_dir, f"throughput_{test_id}_{run_id}.png")
        plt.savefig(filename)
        plt.close()
        chart_files.append(filename)
        
    if "latency" in timeseries:
        # Plot latency over time
        plt.figure(figsize=(10, 6))
        plt.plot(timeseries["latency"]["timestamps"], timeseries["latency"]["values"])
        plt.title(f"Latency over Time - {results.get('testName', 'Unknown Test')}")
        plt.xlabel("Time (seconds)")
        plt.ylabel("Latency (ms)")
        plt.grid(True)
        
        filename = os.path.join(output_dir, f"latency_{test_id}_{run_id}.png")
        plt.savefig(filename)
        plt.close()
        chart_files.append(filename)
        
    # Generate test-specific charts
    if results.get("testType") == "strike":
        if "strikes" in results.get("metrics", {}):
            # Plot strike results as pie chart
            strikes = results["metrics"]["strikes"]
            plt.figure(figsize=(8, 8))
            plt.pie(
                [strikes.get("blocked", 0), strikes.get("allowed", 0)],
                labels=["Blocked", "Allowed"],
                autopct='%1.1f%%',
                colors=['#4CAF50', '#F44336']
            )
            plt.title(f"Strike Results - {results.get('testName', 'Unknown Test')}")
            
            filename = os.path.join(output_dir, f"strikes_{test_id}_{run_id}.png")
            plt.savefig(filename)
            plt.close()
            chart_files.append(filename)
            
    elif results.get("testType") in ["appsim", "clientsim"]:
        if "transactions" in results.get("metrics", {}):
            # Plot transaction results as pie chart
            transactions = results["metrics"]["transactions"]
            plt.figure(figsize=(8, 8))
            plt.pie(
                [transactions.get("successful", 0), transactions.get("failed", 0)],
                labels=["Successful", "Failed"],
                autopct='%1.1f%%',
                colors=['#4CAF50', '#F44336']
            )
            plt.title(f"Transaction Results - {results.get('testName', 'Unknown Test')}")
            
            filename = os.path.join(output_dir, f"transactions_{test_id}_{run_id}.png")
            plt.savefig(filename)
            plt.close()
            chart_files.append(filename)
    
    return chart_files

def compare_charts(bp_api, test_id1: str, run_id1: str, test_id2: str, run_id2: str, 
                  chart_type: str, output_dir: str = "./") -> str:
    """Generate a comparison chart for two test runs
    
    Args:
        bp_api: Breaking Point API instance
        test_id1: First test ID
        run_id1: First run ID
        test_id2: Second test ID
        run_id2: Second run ID
        chart_type: Chart type (throughput, latency, etc.)
        output_dir: Output directory
        
    Returns:
        str: Path to the generated chart file
    """
    results1 = bp_api.get_test_results(test_id1, run_id1)
    results2 = bp_api.get_test_results(test_id2, run_id2)
    
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    if chart_type == "throughput":
        # Plot throughput comparison
        if "timeseries" in results1 and "throughput" in results1["timeseries"] and \
           "timeseries" in results2 and "throughput" in results2["timeseries"]:
            plt.figure(figsize=(10, 6))
            
            # Plot first test
            timestamps1 = results1["timeseries"]["throughput"]["timestamps"]
            values1 = results1["timeseries"]["throughput"]["values"]
            plt.plot(timestamps1, values1, label=f"{results1.get('testName', 'Test 1')}")
            
            # Plot second test
            timestamps2 = results2["timeseries"]["throughput"]["timestamps"]
            values2 = results2["timeseries"]["throughput"]["values"]
            plt.plot(timestamps2, values2, label=f"{results2.get('testName', 'Test 2')}")
            
            plt.title("Throughput Comparison")
            plt.xlabel("Time (seconds)")
            plt.ylabel("Throughput (Mbps)")
            plt.legend()
            plt.grid(True)
            
            filename = os.path.join(output_dir, f"throughput_compare_{test_id1}_{test_id2}.png")
            plt.savefig(filename)
            plt.close()
            return filename
            
    elif chart_type == "latency":
        # Plot latency comparison
        if "timeseries" in results1 and "latency" in results1["timeseries"] and \
           "timeseries" in results2 and "latency" in results2["timeseries"]:
            plt.figure(figsize=(10, 6))
            
            # Plot first test
            timestamps1 = results1["timeseries"]["latency"]["timestamps"]
            values1 = results1["timeseries"]["latency"]["values"]
            plt.plot(timestamps1, values1, label=f"{results1.get('testName', 'Test 1')}")
            
            # Plot second test
            timestamps2 = results2["timeseries"]["latency"]["timestamps"]
            values2 = results2["timeseries"]["latency"]["values"]
            plt.plot(timestamps2, values2, label=f"{results2.get('testName', 'Test 2')}")
            
            plt.title("Latency Comparison")
            plt.xlabel("Time (seconds)")
            plt.ylabel("Latency (ms)")
            plt.legend()
            plt.grid(True)
            
            filename = os.path.join(output_dir, f"latency_compare_{test_id1}_{test_id2}.png")
            plt.savefig(filename)
            plt.close()
            return filename
            
    elif chart_type == "strikes":
        # Plot strike comparison
        if "metrics" in results1 and "strikes" in results1["metrics"] and \
           "metrics" in results2 and "strikes" in results2["metrics"]:
            plt.figure(figsize=(10, 6))
            
            # Prepare data
            tests = [results1.get('testName', 'Test 1'), results2.get('testName', 'Test 2')]
            blocked = [results1["metrics"]["strikes"]["blocked"], results2["metrics"]["strikes"]["blocked"]]
            allowed = [results1["metrics"]["strikes"]["allowed"], results2["metrics"]["strikes"]["allowed"]]
            
            # Create bar chart
            bar_width = 0.35
            index = range(len(tests))
            
            plt.bar(index, blocked, bar_width, label='Blocked', color='#4CAF50')
            plt.bar(index, allowed, bar_width, bottom=blocked, label='Allowed', color='#F44336')
            
            plt.xlabel('Test')
            plt.ylabel('Strike Count')
            plt.title('Strike Results Comparison')
            plt.xticks(index, tests)
            plt.legend()
            
            filename = os.path.join(output_dir, f"strikes_compare_{test_id1}_{test_id2}.png")
            plt.savefig(filename)
            plt.close()
            return filename
            
    elif chart_type == "transactions":
        # Plot transaction comparison
        if "metrics" in results1 and "transactions" in results1["metrics"] and \
           "metrics" in results2 and "transactions" in results2["metrics"]:
            plt.figure(figsize=(10, 6))
            
            # Prepare data
            tests = [results1.get('testName', 'Test 1'), results2.get('testName', 'Test 2')]
            successful = [results1["metrics"]["transactions"]["successful"], 
                         results2["metrics"]["transactions"]["successful"]]
            failed = [results1["metrics"]["transactions"]["failed"], 
                     results2["metrics"]["transactions"]["failed"]]
            
            # Create bar chart
            bar_width = 0.35
            index = range(len(tests))
            
            plt.bar(index, successful, bar_width, label='Successful', color='#4CAF50')
            plt.bar(index, failed, bar_width, bottom=successful, label='Failed', color='#F44336')
            
            plt.xlabel('Test')
            plt.ylabel('Transaction Count')
            plt.title('Transaction Results Comparison')
            plt.xticks(index, tests)
            plt.legend()
            
            filename = os.path.join(output_dir, f"transactions_compare_{test_id1}_{test_id2}.png")
            plt.savefig(filename)
            plt.close()
            return filename
            
    # If we get here, no chart was generated
    return ""
