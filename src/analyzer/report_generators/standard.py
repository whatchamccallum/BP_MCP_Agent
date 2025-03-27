"""
Standard report generator module
"""

from typing import Dict, TextIO, Any

def generate_standard_report(file: TextIO, summary: Dict[str, Any]):
    """Generate a standard HTML report
    
    Args:
        file: File object to write to
        summary: Test result summary
    """
    file.write("""
        <div class="section">
            <h2>Test Information</h2>
            <table>
    """)
    
    file.write(f"""
                <tr><th>Start Time</th><td>{summary['startTime']}</td></tr>
                <tr><th>End Time</th><td>{summary['endTime']}</td></tr>
                <tr><th>Duration</th><td>{summary['duration']} seconds</td></tr>
                <tr><th>Status</th><td>{summary['status']}</td></tr>
            </table>
        </div>
    """)
    
    # Add metrics sections based on test type
    if "throughput" in summary["metrics"]:
        file.write("""
        <div class="section">
            <h2>Performance Metrics</h2>
            <table>
                <tr><th>Metric</th><th>Average</th><th>Maximum</th></tr>
        """)
        
        file.write(f"""
                <tr>
                    <td>Throughput</td>
                    <td>{summary['metrics']['throughput']['average']} {summary['metrics']['throughput']['unit']}</td>
                    <td>{summary['metrics']['throughput']['maximum']} {summary['metrics']['throughput']['unit']}</td>
                </tr>
        """)
        
        if "latency" in summary["metrics"]:
            file.write(f"""
                <tr>
                    <td>Latency</td>
                    <td>{summary['metrics']['latency']['average']} {summary['metrics']['latency']['unit']}</td>
                    <td>{summary['metrics']['latency']['maximum']} {summary['metrics']['latency']['unit']}</td>
                </tr>
            """)
            
        file.write("""
            </table>
        </div>
        """)
    
    if "strikes" in summary["metrics"]:
        file.write(f"""
        <div class="section">
            <h2>Strike Metrics</h2>
            <table>
                <tr><th>Attempted</th><th>Blocked</th><th>Allowed</th><th>Success Rate</th></tr>
                <tr>
                    <td>{summary['metrics']['strikes']['attempted']}</td>
                    <td>{summary['metrics']['strikes']['blocked']}</td>
                    <td>{summary['metrics']['strikes']['allowed']}</td>
                    <td>{summary['metrics']['strikes']['successRate']}%</td>
                </tr>
            </table>
        </div>
        """)
        
    if "transactions" in summary["metrics"]:
        file.write(f"""
        <div class="section">
            <h2>Transaction Metrics</h2>
            <table>
                <tr><th>Attempted</th><th>Successful</th><th>Failed</th><th>Success Rate</th></tr>
                <tr>
                    <td>{summary['metrics']['transactions']['attempted']}</td>
                    <td>{summary['metrics']['transactions']['successful']}</td>
                    <td>{summary['metrics']['transactions']['failed']}</td>
                    <td>{summary['metrics']['transactions']['successRate']}%</td>
                </tr>
            </table>
        </div>
        """)
