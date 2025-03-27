"""
Detailed report generator module
"""

from typing import Dict, TextIO, Any

def generate_detailed_report(file: TextIO, summary: Dict[str, Any], raw_results: Dict[str, Any]):
    """Generate a detailed technical HTML report
    
    Args:
        file: File object to write to
        summary: Test result summary
        raw_results: Raw test results
    """
    # Test Configuration section
    file.write("""
        <div class="section">
            <h2>Test Configuration</h2>
            <table>
    """)
    
    file.write(f"""
                <tr><th>Test Name</th><td>{summary['testName']}</td></tr>
                <tr><th>Test Type</th><td>{summary.get('testType', 'Unknown')}</td></tr>
                <tr><th>Start Time</th><td>{summary['startTime']}</td></tr>
                <tr><th>End Time</th><td>{summary['endTime']}</td></tr>
                <tr><th>Duration</th><td>{summary['duration']} seconds</td></tr>
                <tr><th>Status</th><td>{summary['status']}</td></tr>
    """)
    
    # Add configuration details if available in raw results
    if raw_results and "configuration" in raw_results:
        for key, value in raw_results["configuration"].items():
            if isinstance(value, dict):
                continue  # Skip complex nested objects
            file.write(f"""
                <tr><th>{key}</th><td>{value}</td></tr>
            """)
            
    file.write("""
            </table>
        </div>
    """)
    
    # Standard metrics section (reuse standard report)
    from .standard import generate_standard_report
    generate_standard_report(file, summary)
    
    # Time Series Data section if available
    if raw_results and "timeseries" in raw_results:
        file.write("""
        <div class="section">
            <h2>Time Series Data</h2>
            <p>Time series data is available for plotting charts. Use the chart generation function to visualize this data.</p>
        </div>
        """)
        
    # Detailed Results section based on test type
    if "strikes" in summary["metrics"]:
        generate_detailed_security_section(file, summary, raw_results)
    elif "transactions" in summary["metrics"]:
        generate_detailed_performance_section(file, summary, raw_results)


def generate_detailed_security_section(file: TextIO, summary: Dict[str, Any], raw_results: Dict[str, Any]):
    """Generate detailed security findings section for HTML report
    
    Args:
        file: File object to write to
        summary: Test result summary
        raw_results: Raw test results
    """
    file.write("""
    <div class="section">
        <h2>Detailed Security Findings</h2>
    """)
    
    # If we have detailed strike information in raw results
    if raw_results and "strikes" in raw_results:
        # Group strikes by category
        categories = {}
        for strike in raw_results["strikes"]:
            category = strike.get("category", "Uncategorized")
            if category not in categories:
                categories[category] = {
                    "attempted": 0,
                    "blocked": 0,
                    "allowed": 0,
                    "strikes": []
                }
            
            categories[category]["attempted"] += 1
            if strike.get("blocked", False):
                categories[category]["blocked"] += 1
            else:
                categories[category]["allowed"] += 1
            categories[category]["strikes"].append(strike)
        
        # Display findings by category
        for category, data in categories.items():
            success_rate = (data["blocked"] / data["attempted"] * 100) if data["attempted"] > 0 else 0
            status_class = "pass" if success_rate > 90 else ("warning" if success_rate > 75 else "fail")
            
            file.write(f"""
            <h3>{category}</h3>
            <p>Success Rate: <span class="{status_class}">{success_rate:.2f}%</span></p>
            <p>{data["blocked"]} of {data["attempted"]} attacks blocked</p>
            
            <table>
                <tr><th>Strike Name</th><th>CVSS</th><th>Status</th><th>Details</th></tr>
            """)
            
            # List individual strikes, focusing on allowed ones first
            for strike in sorted(data["strikes"], key=lambda x: x.get("blocked", False)):
                strike_status = "Blocked" if strike.get("blocked", False) else "Allowed"
                status_class = "pass" if strike.get("blocked", False) else "fail"
                cvss = strike.get("cvss", "N/A")
                
                file.write(f"""
                <tr>
                    <td>{strike.get("name", "Unknown")}</td>
                    <td>{cvss}</td>
                    <td class="{status_class}">{strike_status}</td>
                    <td>{strike.get("description", "")}</td>
                </tr>
                """)
            
            file.write("""
            </table>
            """)
        
    else:
        # Basic strike summary if detailed data is not available
        strikes = summary["metrics"]["strikes"]
        file.write(f"""
        <p>Total strikes attempted: {strikes["attempted"]}</p>
        <p>Strikes blocked: {strikes["blocked"]} ({strikes["successRate"]}%)</p>
        <p>Strikes allowed: {strikes["allowed"]}</p>
        <p>Note: Detailed strike information is not available. Run the test with detailed reporting enabled for more information.</p>
        """)
    
    file.write("""
    </div>
    """)


def generate_detailed_performance_section(file: TextIO, summary: Dict[str, Any], raw_results: Dict[str, Any]):
    """Generate detailed performance findings section for HTML report
    
    Args:
        file: File object to write to
        summary: Test result summary
        raw_results: Raw test results
    """
    file.write("""
    <div class="section">
        <h2>Detailed Performance Analysis</h2>
    """)
    
    # If we have detailed performance information
    if raw_results and "performanceStats" in raw_results:
        perf_stats = raw_results["performanceStats"]
        
        # TCP connection stats
        if "tcp" in perf_stats:
            tcp = perf_stats["tcp"]
            file.write("""
            <h3>TCP Connection Statistics</h3>
            <table>
                <tr><th>Metric</th><th>Value</th></tr>
            """)
            
            for key, value in tcp.items():
                file.write(f"""
                <tr><td>{key}</td><td>{value}</td></tr>
                """)
            
            file.write("""
            </table>
            """)
        
        # HTTP stats if available
        if "http" in perf_stats:
            http = perf_stats["http"]
            file.write("""
            <h3>HTTP Statistics</h3>
            <table>
                <tr><th>Metric</th><th>Value</th></tr>
            """)
            
            for key, value in http.items():
                file.write(f"""
                <tr><td>{key}</td><td>{value}</td></tr>
                """)
            
            file.write("""
            </table>
            """)
        
        # Resource utilization
        if "resources" in perf_stats:
            resources = perf_stats["resources"]
            file.write("""
            <h3>Resource Utilization</h3>
            <table>
                <tr><th>Resource</th><th>Utilization</th></tr>
            """)
            
            for key, value in resources.items():
                file.write(f"""
                <tr><td>{key}</td><td>{value}</td></tr>
                """)
            
            file.write("""
            </table>
            """)
    
    # Transaction breakdown
    if "transactions" in summary["metrics"]:
        transactions = summary["metrics"]["transactions"]
        file.write(f"""
        <h3>Transaction Summary</h3>
        <p>Total transactions: {transactions["attempted"]}</p>
        <p>Successful: {transactions["successful"]} ({transactions["successRate"]}%)</p>
        <p>Failed: {transactions["failed"]}</p>
        """)
        
        # If we have detailed transaction information
        if raw_results and "transactions" in raw_results and isinstance(raw_results["transactions"], list):
            # Group transactions by type/endpoint
            tx_types = {}
            for tx in raw_results["transactions"]:
                tx_type = tx.get("type", "Unknown")
                if tx_type not in tx_types:
                    tx_types[tx_type] = {
                        "attempted": 0,
                        "successful": 0,
                        "failed": 0
                    }
                
                tx_types[tx_type]["attempted"] += 1
                if tx.get("successful", False):
                    tx_types[tx_type]["successful"] += 1
                else:
                    tx_types[tx_type]["failed"] += 1
            
            file.write("""
            <h3>Transaction Breakdown by Type</h3>
            <table>
                <tr><th>Transaction Type</th><th>Attempted</th><th>Successful</th><th>Failed</th><th>Success Rate</th></tr>
            """)
            
            for tx_type, stats in tx_types.items():
                success_rate = (stats["successful"] / stats["attempted"] * 100) if stats["attempted"] > 0 else 0
                status_class = "pass" if success_rate > 95 else ("warning" if success_rate > 80 else "fail")
                
                file.write(f"""
                <tr>
                    <td>{tx_type}</td>
                    <td>{stats["attempted"]}</td>
                    <td>{stats["successful"]}</td>
                    <td>{stats["failed"]}</td>
                    <td class="{status_class}">{success_rate:.2f}%</td>
                </tr>
                """)
            
            file.write("""
            </table>
            """)
    
    file.write("""
    </div>
    """)
