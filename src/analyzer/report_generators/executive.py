"""
Executive report generator module
"""

from typing import Dict, TextIO, Any

def generate_executive_report(file: TextIO, summary: Dict[str, Any], raw_results: Dict[str, Any]):
    """Generate an executive summary HTML report
    
    Args:
        file: File object to write to
        summary: Test result summary
        raw_results: Raw test results
    """
    # Executive Summary section
    file.write("""
        <div class="section">
            <h2>Executive Summary</h2>
    """)
    
    # Overall test status with color coding
    status_class = "pass" if summary["status"] == "completed" else "fail"
    file.write(f"""
            <p class="summary">Test Status: <span class="{status_class}">{summary["status"].upper()}</span></p>
    """)
    
    # Test duration and timing
    file.write(f"""
            <p>Test Duration: {summary["duration"]} seconds</p>
            <p>Executed: {summary["startTime"]} to {summary["endTime"]}</p>
    """)
    
    # Key findings based on test type
    file.write("""
            <h3>Key Findings</h3>
    """)
    
    if "strikes" in summary["metrics"]:
        # Security test summary
        strikes = summary["metrics"]["strikes"]
        success_rate = strikes["successRate"]
        status_class = "pass" if success_rate > 90 else ("warning" if success_rate > 75 else "fail")
        
        file.write(f"""
            <p>Security Test Results: <span class="{status_class}">{success_rate}% of attacks blocked</span></p>
            <p>{strikes["blocked"]} attacks blocked out of {strikes["attempted"]} attempted</p>
            <p>{strikes["allowed"]} potential vulnerabilities identified</p>
        """)
        
        # Risk assessment
        risk_level = "Low" if success_rate > 90 else ("Medium" if success_rate > 75 else "High")
        risk_class = "pass" if risk_level == "Low" else ("warning" if risk_level == "Medium" else "fail")
        
        file.write(f"""
            <h3>Risk Assessment</h3>
            <p>Overall Risk Level: <span class="{risk_class}">{risk_level}</span></p>
        """)
        
    elif "transactions" in summary["metrics"]:
        # Application/client simulation summary
        transactions = summary["metrics"]["transactions"]
        success_rate = transactions["successRate"]
        status_class = "pass" if success_rate > 95 else ("warning" if success_rate > 80 else "fail")
        
        file.write(f"""
            <p>Application Performance: <span class="{status_class}">{success_rate}% success rate</span></p>
            <p>{transactions["successful"]} successful transactions out of {transactions["attempted"]} attempted</p>
            <p>{transactions["failed"]} failed transactions</p>
        """)
        
        # Performance assessment
        if "throughput" in summary["metrics"] and "latency" in summary["metrics"]:
            throughput = summary["metrics"]["throughput"]["average"]
            latency = summary["metrics"]["latency"]["average"]
            
            file.write(f"""
                <h3>Performance Assessment</h3>
                <p>Average Throughput: {throughput} {summary["metrics"]["throughput"]["unit"]}</p>
                <p>Average Latency: {latency} {summary["metrics"]["latency"]["unit"]}</p>
            """)
    
    file.write("""
        </div>
    """)
    
    # Recommendations section
    file.write("""
        <div class="section">
            <h2>Recommendations</h2>
            <ul>
    """)
    
    if "strikes" in summary["metrics"]:
        # Security recommendations
        if summary["metrics"]["strikes"]["allowed"] > 0:
            file.write("""
                <li>Review and address the identified vulnerabilities</li>
                <li>Consider updating security policies to address the attack vectors</li>
                <li>Schedule a follow-up security test after implementing fixes</li>
            """)
        else:
            file.write("""
                <li>Maintain current security posture</li>
                <li>Schedule regular security testing to ensure continued protection</li>
                <li>Consider expanding test coverage to include additional attack vectors</li>
            """)
    elif "transactions" in summary["metrics"]:
        # Performance recommendations
        if summary["metrics"]["transactions"]["successRate"] < 95:
            file.write("""
                <li>Investigate causes of failed transactions</li>
                <li>Consider optimizing application response times</li>
                <li>Evaluate resource allocation and scaling options</li>
            """)
        else:
            file.write("""
                <li>Monitor application performance under varying load conditions</li>
                <li>Consider stress testing to determine maximum capacity</li>
                <li>Implement regular performance testing in the CI/CD pipeline</li>
            """)
    
    file.write("""
            </ul>
        </div>
    """)
