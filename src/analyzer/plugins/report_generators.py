"""
Report generator plugins for Breaking Point test results.
"""
import os
from datetime import datetime
from typing import Dict, List, Any, TextIO, Optional, cast

from .base import ReportGenerator, TestSummary

class StandardReportGenerator(ReportGenerator):
    """Generates standard reports for test results"""
    
    def generate(self, summary: TestSummary, raw_results: Dict[str, Any], 
                output_format: str, output_file: str) -> str:
        """Generate a standard report
        
        Args:
            summary: Test summary data
            raw_results: Raw test results
            output_format: Output format (html, csv, pdf)
            output_file: Path to output file
            
        Returns:
            str: Path to generated report
        """
        if output_format == "html":
            return self._generate_html(summary, raw_results, output_file)
        elif output_format == "csv":
            return self._generate_csv(summary, raw_results, output_file)
        else:
            raise ValueError(f"Unsupported output format: {output_format}")
    
    def _generate_html(self, summary: TestSummary, raw_results: Dict[str, Any], output_file: str) -> str:
        """Generate an HTML report
        
        Args:
            summary: Test summary data
            raw_results: Raw test results
            output_file: Path to output file
            
        Returns:
            str: Path to generated report
        """
        with open(output_file, "w") as f:
            # Write HTML header
            f.write(f"""
            <html>
            <head>
                <title>Test Report: {summary['testName']} - Standard</title>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 20px; }}
                    h1 {{ color: #333366; }}
                    h2 {{ color: #333366; margin-top: 30px; }}
                    h3 {{ color: #666666; }}
                    .section {{ margin-bottom: 20px; padding: 10px; border: 1px solid #ddd; border-radius: 5px; }}
                    .header {{ background-color: #f8f8f8; padding: 15px; border-bottom: 2px solid #ddd; }}
                    .summary {{ font-size: 1.1em; margin: 15px 0; }}
                    .pass {{ color: green; }}
                    .fail {{ color: red; }}
                    .warning {{ color: orange; }}
                    table {{ border-collapse: collapse; width: 100%; margin-bottom: 20px; }}
                    th, td {{ padding: 8px; text-align: left; border-bottom: 1px solid #ddd; }}
                    th {{ background-color: #f2f2f2; }}
                    .chart {{ margin: 20px 0; }}
                    .footer {{ margin-top: 30px; font-size: 0.8em; color: #666; text-align: center; }}
                </style>
            </head>
            <body>
                <div class="header">
                    <h1>Test Report: {summary['testName']}</h1>
                    <p>Report Type: Standard</p>
                    <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                </div>
            """)
            
            # Test Overview section
            self.write_html_section(f, "Test Overview", {
                "Test ID": summary["testId"],
                "Run ID": summary["runId"],
                "Test Type": summary["testType"],
                "Start Time": summary["startTime"],
                "End Time": summary["endTime"],
                "Duration": f"{summary['duration']} seconds",
                "Status": summary["status"]
            })
            
            # Performance metrics section
            if "throughput" in summary["metrics"] or "latency" in summary["metrics"]:
                f.write("<h2>Performance Metrics</h2>\n<div class='section'>\n")
                f.write("<table>\n<tr><th>Metric</th><th>Average</th><th>Maximum</th></tr>\n")
                
                if "throughput" in summary["metrics"]:
                    throughput = summary["metrics"]["throughput"]
                    f.write(f"<tr><td>Throughput</td><td>{throughput['average']} {throughput['unit']}</td><td>{throughput['maximum']} {throughput['unit']}</td></tr>\n")
                
                if "latency" in summary["metrics"]:
                    latency = summary["metrics"]["latency"]
                    f.write(f"<tr><td>Latency</td><td>{latency['average']} {latency['unit']}</td><td>{latency['maximum']} {latency['unit']}</td></tr>\n")
                
                f.write("</table>\n</div>\n")
            
            # Strike metrics section for security tests
            if "strikes" in summary["metrics"]:
                strikes = summary["metrics"]["strikes"]
                self.write_html_section(f, "Security Test Results", {
                    "Strikes Attempted": strikes["attempted"],
                    "Strikes Blocked": strikes["blocked"],
                    "Strikes Allowed": strikes["allowed"],
                    "Protection Success Rate": f"{strikes['successRate']}%"
                })
            
            # Transaction metrics section for application tests
            if "transactions" in summary["metrics"]:
                transactions = summary["metrics"]["transactions"]
                self.write_html_section(f, "Application Test Results", {
                    "Transactions Attempted": transactions["attempted"],
                    "Transactions Successful": transactions["successful"],
                    "Transactions Failed": transactions["failed"],
                    "Transaction Success Rate": f"{transactions['successRate']}%"
                })
            
            # Footer
            f.write("""
                <div class="footer">
                    <p>Generated by Breaking Point MCP Agent</p>
                </div>
            </body>
            </html>
            """)
        
        return output_file
    
    def _generate_csv(self, summary: TestSummary, raw_results: Dict[str, Any], output_file: str) -> str:
        """Generate a CSV report
        
        Args:
            summary: Test summary data
            raw_results: Raw test results
            output_file: Path to output file
            
        Returns:
            str: Path to generated report
        """
        with open(output_file, "w") as f:
            f.write(f"Test Name,{summary['testName']}\n")
            f.write(f"Report Type,Standard\n")
            f.write(f"Generated,{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Start Time,{summary['startTime']}\n")
            f.write(f"End Time,{summary['endTime']}\n")
            f.write(f"Duration,{summary['duration']} seconds\n")
            f.write(f"Status,{summary['status']}\n\n")
            
            # Write metrics based on test type
            if "throughput" in summary["metrics"]:
                f.write("Performance Metrics\n")
                f.write("Metric,Average,Maximum\n")
                throughput = summary["metrics"]["throughput"]
                f.write(f"Throughput,{throughput['average']} {throughput['unit']},{throughput['maximum']} {throughput['unit']}\n")
                
                if "latency" in summary["metrics"]:
                    latency = summary["metrics"]["latency"]
                    f.write(f"Latency,{latency['average']} {latency['unit']},{latency['maximum']} {latency['unit']}\n")
            
            if "strikes" in summary["metrics"]:
                strikes = summary["metrics"]["strikes"]
                f.write("\nStrike Metrics\n")
                f.write("Attempted,Blocked,Allowed,Success Rate\n")
                f.write(f"{strikes['attempted']},{strikes['blocked']},{strikes['allowed']},{strikes['successRate']}%\n")
            
            if "transactions" in summary["metrics"]:
                transactions = summary["metrics"]["transactions"]
                f.write("\nTransaction Metrics\n")
                f.write("Attempted,Successful,Failed,Success Rate\n")
                f.write(f"{transactions['attempted']},{transactions['successful']},{transactions['failed']},{transactions['successRate']}%\n")
                
        return output_file

class ExecutiveReportGenerator(ReportGenerator):
    """Generates executive reports for test results"""
    
    def generate(self, summary: TestSummary, raw_results: Dict[str, Any], 
                output_format: str, output_file: str) -> str:
        """Generate an executive report
        
        Args:
            summary: Test summary data
            raw_results: Raw test results
            output_format: Output format (html, csv, pdf)
            output_file: Path to output file
            
        Returns:
            str: Path to generated report
        """
        if output_format == "html":
            return self._generate_html(summary, raw_results, output_file)
        elif output_format == "csv":
            return self._generate_csv(summary, raw_results, output_file)
        else:
            raise ValueError(f"Unsupported output format: {output_format}")
    
    def _generate_html(self, summary: TestSummary, raw_results: Dict[str, Any], output_file: str) -> str:
        """Generate an HTML executive report
        
        Args:
            summary: Test summary data
            raw_results: Raw test results
            output_file: Path to output file
            
        Returns:
            str: Path to generated report
        """
        with open(output_file, "w") as f:
            # Write HTML header with executive styling
            f.write(f"""
            <html>
            <head>
                <title>Executive Report: {summary['testName']}</title>
                <style>
                    body {{ font-family: 'Segoe UI', Arial, sans-serif; margin: 20px; color: #333; }}
                    h1 {{ color: #00205B; border-bottom: 2px solid #00205B; padding-bottom: 10px; }}
                    h2 {{ color: #00205B; margin-top: 30px; }}
                    .section {{ margin-bottom: 30px; padding: 15px; border-radius: 8px; box-shadow: 0 1px 5px rgba(0,0,0,0.1); }}
                    .header {{ background-color: #f8f8f8; padding: 20px; }}
                    .status {{ font-size: 1.2em; margin: 20px 0; padding: 10px; border-radius: 5px; }}
                    .status.pass {{ background-color: #e6f4ea; color: #137333; }}
                    .status.fail {{ background-color: #fce8e6; color: #c5221f; }}
                    .status.warning {{ background-color: #fef7e0; color: #b06000; }}
                    .metric-card {{ display: inline-block; width: 200px; margin: 10px; padding: 15px; 
                                    border-radius: 8px; box-shadow: 0 1px 5px rgba(0,0,0,0.1); text-align: center; }}
                    .metric-value {{ font-size: 24px; font-weight: bold; margin: 10px 0; }}
                    .metric-label {{ font-size: 14px; color: #666; }}
                    .footer {{ margin-top: 40px; font-size: 0.8em; color: #666; text-align: center; }}
                </style>
            </head>
            <body>
                <div class="header">
                    <h1>Executive Summary: {summary['testName']}</h1>
                    <p>Test Type: {summary['testType']}</p>
                    <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                </div>
            """)
            
            # Overall status section
            status_class = "pass" if summary["status"] == "completed" else "warning" if summary["status"] == "stopped" else "fail"
            f.write(f"""
                <div class="section">
                    <h2>Overall Result</h2>
                    <div class="status {status_class}">
                        Test Status: {summary["status"]}
                    </div>
                    <p>Duration: {summary["duration"]} seconds</p>
                </div>
            """)
            
            # Key metrics section with visual cards
            f.write('<div class="section"><h2>Key Metrics</h2><div class="metrics-container">')
            
            # Add throughput card if available
            if "throughput" in summary["metrics"]:
                throughput = summary["metrics"]["throughput"]
                f.write(f"""
                    <div class="metric-card">
                        <div class="metric-label">Average Throughput</div>
                        <div class="metric-value">{throughput['average']} {throughput['unit']}</div>
                    </div>
                """)
            
            # Add latency card if available
            if "latency" in summary["metrics"]:
                latency = summary["metrics"]["latency"]
                f.write(f"""
                    <div class="metric-card">
                        <div class="metric-label">Average Latency</div>
                        <div class="metric-value">{latency['average']} {latency['unit']}</div>
                    </div>
                """)
            
            # Add strike success rate card if available
            if "strikes" in summary["metrics"]:
                strikes = summary["metrics"]["strikes"]
                f.write(f"""
                    <div class="metric-card">
                        <div class="metric-label">Security Success Rate</div>
                        <div class="metric-value">{strikes['successRate']}%</div>
                    </div>
                """)
            
            # Add transaction success rate card if available
            if "transactions" in summary["metrics"]:
                transactions = summary["metrics"]["transactions"]
                f.write(f"""
                    <div class="metric-card">
                        <div class="metric-label">Transaction Success Rate</div>
                        <div class="metric-value">{transactions['successRate']}%</div>
                    </div>
                """)
                
            f.write('</div></div>')
            
            # Executive conclusions
            f.write('<div class="section"><h2>Executive Conclusions</h2>')
            
            if summary["testType"] == "strike":
                # Security test conclusions
                success_rate = summary["metrics"].get("strikes", {}).get("successRate", 0)
                if success_rate >= 90:
                    conclusion = "The security test indicates strong protection capabilities. The system effectively blocked most security threats."
                elif success_rate >= 70:
                    conclusion = "The security test indicates adequate protection, but there is room for improvement in threat mitigation."
                else:
                    conclusion = "The security test reveals significant vulnerabilities. Immediate remediation actions are recommended."
                
                f.write(f"<p>{conclusion}</p>")
                
            elif summary["testType"] in ["appsim", "clientsim"]:
                # Application test conclusions
                success_rate = summary["metrics"].get("transactions", {}).get("successRate", 0)
                avg_throughput = summary["metrics"].get("throughput", {}).get("average", 0)
                
                if success_rate >= 95 and avg_throughput > 0:
                    conclusion = "The application performance is excellent, with high transaction success rates and good throughput."
                elif success_rate >= 80:
                    conclusion = "The application performance is acceptable but shows room for optimization to improve transaction success rates."
                else:
                    conclusion = "The application performance test indicates significant issues with reliability and/or performance."
                    
                f.write(f"<p>{conclusion}</p>")
                
            f.write('</div>')
            
            # Footer
            f.write("""
                <div class="footer">
                    <p>Generated by Breaking Point MCP Agent | CONFIDENTIAL</p>
                </div>
            </body>
            </html>
            """)
        
        return output_file
    
    def _generate_csv(self, summary: TestSummary, raw_results: Dict[str, Any], output_file: str) -> str:
        """Generate a CSV executive report
        
        Args:
            summary: Test summary data
            raw_results: Raw test results
            output_file: Path to output file
            
        Returns:
            str: Path to generated report
        """
        with open(output_file, "w") as f:
            f.write(f"Test Name,{summary['testName']}\n")
            f.write(f"Report Type,Executive Summary\n")
            f.write(f"Generated,{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            f.write("OVERALL RESULT\n")
            f.write(f"Status,{summary['status']}\n")
            f.write(f"Duration,{summary['duration']} seconds\n\n")
            
            f.write("KEY METRICS\n")
            if "throughput" in summary["metrics"]:
                throughput = summary["metrics"]["throughput"]
                f.write(f"Average Throughput,{throughput['average']} {throughput['unit']}\n")
            
            if "latency" in summary["metrics"]:
                latency = summary["metrics"]["latency"]
                f.write(f"Average Latency,{latency['average']} {latency['unit']}\n")
                
            if "strikes" in summary["metrics"]:
                strikes = summary["metrics"]["strikes"]
                f.write(f"Security Success Rate,{strikes['successRate']}%\n")
                
            if "transactions" in summary["metrics"]:
                transactions = summary["metrics"]["transactions"]
                f.write(f"Transaction Success Rate,{transactions['successRate']}%\n")
                
        return output_file

class DetailedReportGenerator(ReportGenerator):
    """Generates detailed technical reports for test results"""
    
    def generate(self, summary: TestSummary, raw_results: Dict[str, Any], 
                output_format: str, output_file: str) -> str:
        """Generate a detailed technical report
        
        Args:
            summary: Test summary data
            raw_results: Raw test results
            output_format: Output format (html, csv, pdf)
            output_file: Path to output file
            
        Returns:
            str: Path to generated report
        """
        if output_format == "html":
            return self._generate_html(summary, raw_results, output_file)
        elif output_format == "csv":
            return self._generate_csv(summary, raw_results, output_file)
        else:
            raise ValueError(f"Unsupported output format: {output_format}")
    
    def _generate_html(self, summary: TestSummary, raw_results: Dict[str, Any], output_file: str) -> str:
        """Generate a detailed HTML report
        
        Args:
            summary: Test summary data
            raw_results: Raw test results
            output_file: Path to output file
            
        Returns:
            str: Path to generated report
        """
        with open(output_file, "w") as f:
            # Write HTML header with technical styling
            f.write(f"""
            <html>
            <head>
                <title>Detailed Technical Report: {summary['testName']}</title>
                <style>
                    body {{ font-family: 'Courier New', monospace; margin: 20px; color: #333; }}
                    h1 {{ color: #0066cc; }}
                    h2 {{ color: #0066cc; margin-top: 30px; border-top: 1px solid #ddd; padding-top: 10px; }}
                    h3 {{ color: #333; margin-top: 20px; }}
                    .section {{ margin-bottom: 20px; padding: 10px; border: 1px solid #ddd; border-radius: 5px; }}
                    .header {{ background-color: #f0f8ff; padding: 15px; }}
                    pre {{ background-color: #f5f5f5; padding: 10px; border-radius: 5px; overflow-x: auto; }}
                    table {{ border-collapse: collapse; width: 100%; margin-bottom: 20px; }}
                    th, td {{ padding: 8px; text-align: left; border: 1px solid #ddd; }}
                    th {{ background-color: #f2f2f2; }}
                    .footer {{ margin-top: 30px; font-size: 0.8em; color: #666; text-align: center; }}
                    .collapsed {{ display: none; }}
                    .toggle-btn {{ cursor: pointer; color: #0066cc; }}
                </style>
                <script>
                    function toggleSection(id) {{
                        var section = document.getElementById(id);
                        if (section.classList.contains('collapsed')) {{
                            section.classList.remove('collapsed');
                        }} else {{
                            section.classList.add('collapsed');
                        }}
                    }}
                </script>
            </head>
            <body>
                <div class="header">
                    <h1>Detailed Technical Report: {summary['testName']}</h1>
                    <p>Test Type: {summary['testType']}</p>
                    <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                </div>
            """)
            
            # Test configuration section
            f.write('<h2>Test Configuration</h2><div class="section">')
            f.write("<table>")
            f.write("<tr><th>Parameter</th><th>Value</th></tr>")
            f.write(f"<tr><td>Test ID</td><td>{summary['testId']}</td></tr>")
            f.write(f"<tr><td>Run ID</td><td>{summary['runId']}</td></tr>")
            f.write(f"<tr><td>Test Type</td><td>{summary['testType']}</td></tr>")
            f.write(f"<tr><td>Start Time</td><td>{summary['startTime']}</td></tr>")
            f.write(f"<tr><td>End Time</td><td>{summary['endTime']}</td></tr>")
            f.write(f"<tr><td>Duration</td><td>{summary['duration']} seconds</td></tr>")
            f.write(f"<tr><td>Status</td><td>{summary['status']}</td></tr>")
            
            # Include configuration from raw results if available
            if "configuration" in raw_results:
                config = raw_results["configuration"]
                for key, value in config.items():
                    if isinstance(value, dict):
                        # For nested dictionaries, create a toggleable JSON section
                        f.write(f"<tr><td>{key}</td><td>")
                        f.write(f'<span class="toggle-btn" onclick="toggleSection(\'{key}\')">Show/Hide Details</span>')
                        f.write(f'<pre id="{key}" class="collapsed">{str(value)}</pre>')
                        f.write("</td></tr>")
                    else:
                        f.write(f"<tr><td>{key}</td><td>{value}</td></tr>")
                
            f.write("</table></div>")
            
            # Detailed metrics section
            f.write('<h2>Performance Metrics</h2><div class="section">')
            
            # Add throughput and latency data
            if "throughput" in summary["metrics"] or "latency" in summary["metrics"]:
                f.write("<table>")
                f.write("<tr><th>Metric</th><th>Average</th><th>Maximum</th><th>Minimum</th><th>Standard Deviation</th></tr>")
                
                if "throughput" in summary["metrics"]:
                    throughput = summary["metrics"]["throughput"]
                    f.write(f"<tr><td>Throughput</td><td>{throughput['average']} {throughput['unit']}</td>")
                    f.write(f"<td>{throughput['maximum']} {throughput['unit']}</td>")
                    
                    # Include additional data from raw results if available
                    throughput_raw = raw_results.get("metrics", {}).get("throughput", {})
                    min_val = throughput_raw.get("minimum", "N/A")
                    std_dev = throughput_raw.get("standardDeviation", "N/A")
                    
                    f.write(f"<td>{min_val} {throughput.get('unit', '')}</td>")
                    f.write(f"<td>{std_dev}</td></tr>")
                
                if "latency" in summary["metrics"]:
                    latency = summary["metrics"]["latency"]
                    f.write(f"<tr><td>Latency</td><td>{latency['average']} {latency['unit']}</td>")
                    f.write(f"<td>{latency['maximum']} {latency['unit']}</td>")
                    
                    # Include additional data from raw results if available
                    latency_raw = raw_results.get("metrics", {}).get("latency", {})
                    min_val = latency_raw.get("minimum", "N/A")
                    std_dev = latency_raw.get("standardDeviation", "N/A")
                    
                    f.write(f"<td>{min_val} {latency.get('unit', '')}</td>")
                    f.write(f"<td>{std_dev}</td></tr>")
                    
                f.write("</table>")
            
            # Include time series data if available
            if "timeSeriesData" in raw_results:
                f.write('<h3>Time Series Data</h3>')
                f.write('<p><span class="toggle-btn" onclick="toggleSection(\'timeSeriesData\')">Show/Hide Time Series Data</span></p>')
                f.write('<div id="timeSeriesData" class="collapsed">')
                f.write('<table><tr><th>Timestamp</th><th>Throughput</th><th>Latency</th></tr>')
                
                time_series = raw_results["timeSeriesData"]
                for point in time_series:
                    f.write(f"<tr><td>{point.get('timestamp', 'N/A')}</td>")
                    f.write(f"<td>{point.get('throughput', 'N/A')}</td>")
                    f.write(f"<td>{point.get('latency', 'N/A')}</td></tr>")
                
                f.write('</table></div>')
            
            f.write('</div>')
            
            # Add test-type specific detailed sections
            if summary["testType"] == "strike":
                self._add_strike_details(f, summary, raw_results)
            elif summary["testType"] in ["appsim", "clientsim"]:
                self._add_transaction_details(f, summary, raw_results)
            
            # Raw results section
            f.write('<h2>Raw Test Results</h2>')
            f.write('<p><span class="toggle-btn" onclick="toggleSection(\'rawResults\')">Show/Hide Raw Results</span></p>')
            f.write('<pre id="rawResults" class="collapsed">')
            f.write(str(raw_results))
            f.write('</pre>')
            
            # Footer
            f.write("""
                <div class="footer">
                    <p>Generated by Breaking Point MCP Agent | Technical Report</p>
                </div>
            </body>
            </html>
            """)
            
        return output_file
    
    def _add_strike_details(self, f: TextIO, summary: TestSummary, raw_results: Dict[str, Any]) -> None:
        """Add strike test details to the report
        
        Args:
            f: File object to write to
            summary: Test summary data
            raw_results: Raw test results
        """
        f.write('<h2>Security Test Details</h2><div class="section">')
        
        if "strikes" in summary["metrics"]:
            strikes = summary["metrics"]["strikes"]
            f.write("<table>")
            f.write("<tr><th>Parameter</th><th>Value</th></tr>")
            f.write(f"<tr><td>Strikes Attempted</td><td>{strikes['attempted']}</td></tr>")
            f.write(f"<tr><td>Strikes Blocked</td><td>{strikes['blocked']}</td></tr>")
            f.write(f"<tr><td>Strikes Allowed</td><td>{strikes['allowed']}</td></tr>")
            f.write(f"<tr><td>Protection Success Rate</td><td>{strikes['successRate']}%</td></tr>")
            f.write("</table>")
            
            # Add detailed strike information if available
            if "strikeResults" in raw_results:
                f.write('<h3>Individual Strike Results</h3>')
                f.write('<p><span class="toggle-btn" onclick="toggleSection(\'strikeResults\')">Show/Hide Strike Details</span></p>')
                f.write('<div id="strikeResults" class="collapsed">')
                f.write('<table><tr><th>Strike ID</th><th>Name</th><th>Category</th><th>Result</th><th>Details</th></tr>')
                
                for strike in raw_results["strikeResults"]:
                    strike_id = strike.get("id", "N/A")
                    name = strike.get("name", "N/A")
                    category = strike.get("category", "N/A")
                    result = strike.get("result", "N/A")
                    details = strike.get("details", "N/A")
                    
                    f.write(f"<tr><td>{strike_id}</td><td>{name}</td><td>{category}</td>")
                    f.write(f"<td>{result}</td><td>{details}</td></tr>")
                
                f.write('</table></div>')
                
        f.write('</div>')
    
    def _add_transaction_details(self, f: TextIO, summary: TestSummary, raw_results: Dict[str, Any]) -> None:
        """Add transaction test details to the report
        
        Args:
            f: File object to write to
            summary: Test summary data
            raw_results: Raw test results
        """
        f.write('<h2>Application Test Details</h2><div class="section">')
        
        if "transactions" in summary["metrics"]:
            transactions = summary["metrics"]["transactions"]
            f.write("<table>")
            f.write("<tr><th>Parameter</th><th>Value</th></tr>")
            f.write(f"<tr><td>Transactions Attempted</td><td>{transactions['attempted']}</td></tr>")
            f.write(f"<tr><td>Transactions Successful</td><td>{transactions['successful']}</td></tr>")
            f.write(f"<tr><td>Transactions Failed</td><td>{transactions['failed']}</td></tr>")
            f.write(f"<tr><td>Transaction Success Rate</td><td>{transactions['successRate']}%</td></tr>")
            f.write("</table>")
            
            # Add detailed transaction information if available
            if "transactionResults" in raw_results:
                f.write('<h3>Transaction Results by Type</h3>')
                f.write('<p><span class="toggle-btn" onclick="toggleSection(\'transactionResults\')">Show/Hide Transaction Details</span></p>')
                f.write('<div id="transactionResults" class="collapsed">')
                f.write('<table><tr><th>Transaction Type</th><th>Attempted</th><th>Successful</th><th>Failed</th><th>Success Rate</th></tr>')
                
                for tx_type, tx_data in raw_results["transactionResults"].items():
                    attempted = tx_data.get("attempted", 0)
                    successful = tx_data.get("successful", 0)
                    failed = tx_data.get("failed", 0)
                    success_rate = 0
                    if attempted > 0:
                        success_rate = (successful / attempted) * 100
                        
                    f.write(f"<tr><td>{tx_type}</td><td>{attempted}</td><td>{successful}</td>")
                    f.write(f"<td>{failed}</td><td>{success_rate:.2f}%</td></tr>")
                
                f.write('</table></div>')
                
        f.write('</div>')
    
    def _generate_csv(self, summary: TestSummary, raw_results: Dict[str, Any], output_file: str) -> str:
        """Generate a detailed CSV report
        
        Args:
            summary: Test summary data
            raw_results: Raw test results
            output_file: Path to output file
            
        Returns:
            str: Path to generated report
        """
        with open(output_file, "w") as f:
            f.write(f"Test Name,{summary['testName']}\n")
            f.write(f"Report Type,Detailed Technical Report\n")
            f.write(f"Generated,{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            # Test configuration
            f.write("TEST CONFIGURATION\n")
            f.write(f"Test ID,{summary['testId']}\n")
            f.write(f"Run ID,{summary['runId']}\n")
            f.write(f"Test Type,{summary['testType']}\n")
            f.write(f"Start Time,{summary['startTime']}\n")
            f.write(f"End Time,{summary['endTime']}\n")
            f.write(f"Duration,{summary['duration']} seconds\n")
            f.write(f"Status,{summary['status']}\n\n")
            
            # Performance metrics
            f.write("PERFORMANCE METRICS\n")
            f.write("Metric,Average,Maximum,Minimum,Standard Deviation\n")
            
            if "throughput" in summary["metrics"]:
                throughput = summary["metrics"]["throughput"]
                throughput_raw = raw_results.get("metrics", {}).get("throughput", {})
                min_val = throughput_raw.get("minimum", "N/A")
                std_dev = throughput_raw.get("standardDeviation", "N/A")
                
                f.write(f"Throughput,{throughput['average']} {throughput['unit']},{throughput['maximum']} {throughput['unit']},")
                f.write(f"{min_val} {throughput.get('unit', '')},{std_dev}\n")
            
            if "latency" in summary["metrics"]:
                latency = summary["metrics"]["latency"]
                latency_raw = raw_results.get("metrics", {}).get("latency", {})
                min_val = latency_raw.get("minimum", "N/A")
                std_dev = latency_raw.get("standardDeviation", "N/A")
                
                f.write(f"Latency,{latency['average']} {latency['unit']},{latency['maximum']} {latency['unit']},")
                f.write(f"{min_val} {latency.get('unit', '')},{std_dev}\n")
            
            f.write("\n")
            
            # Test-type specific sections
            if summary["testType"] == "strike":
                self._write_csv_strike_details(f, summary, raw_results)
            elif summary["testType"] in ["appsim", "clientsim"]:
                self._write_csv_transaction_details(f, summary, raw_results)
                
            # Time series data if available
            if "timeSeriesData" in raw_results:
                f.write("\nTIME SERIES DATA\n")
                f.write("Timestamp,Throughput,Latency\n")
                
                for point in raw_results["timeSeriesData"]:
                    timestamp = point.get('timestamp', 'N/A')
                    throughput = point.get('throughput', 'N/A')
                    latency = point.get('latency', 'N/A')
                    f.write(f"{timestamp},{throughput},{latency}\n")
                
        return output_file
    
    def _write_csv_strike_details(self, f: TextIO, summary: TestSummary, raw_results: Dict[str, Any]) -> None:
        """Write strike test details to CSV
        
        Args:
            f: File object to write to
            summary: Test summary data
            raw_results: Raw test results
        """
        f.write("SECURITY TEST DETAILS\n")
        
        if "strikes" in summary["metrics"]:
            strikes = summary["metrics"]["strikes"]
            f.write(f"Strikes Attempted,{strikes['attempted']}\n")
            f.write(f"Strikes Blocked,{strikes['blocked']}\n")
            f.write(f"Strikes Allowed,{strikes['allowed']}\n")
            f.write(f"Protection Success Rate,{strikes['successRate']}%\n\n")
            
            # Add detailed strike information if available
            if "strikeResults" in raw_results:
                f.write("INDIVIDUAL STRIKE RESULTS\n")
                f.write("Strike ID,Name,Category,Result,Details\n")
                
                for strike in raw_results["strikeResults"]:
                    strike_id = strike.get("id", "N/A")
                    name = strike.get("name", "N/A")
                    category = strike.get("category", "N/A")
                    result = strike.get("result", "N/A")
                    details = strike.get("details", "N/A")
                    
                    # Escape any commas in the fields to avoid CSV format issues
                    name = f'"{name}"' if "," in name else name
                    category = f'"{category}"' if "," in category else category
                    details = f'"{details}"' if "," in details else details
                    
                    f.write(f"{strike_id},{name},{category},{result},{details}\n")
                
    def _write_csv_transaction_details(self, f: TextIO, summary: TestSummary, raw_results: Dict[str, Any]) -> None:
        """Write transaction test details to CSV
        
        Args:
            f: File object to write to
            summary: Test summary data
            raw_results: Raw test results
        """
        f.write("APPLICATION TEST DETAILS\n")
        
        if "transactions" in summary["metrics"]:
            transactions = summary["metrics"]["transactions"]
            f.write(f"Transactions Attempted,{transactions['attempted']}\n")
            f.write(f"Transactions Successful,{transactions['successful']}\n")
            f.write(f"Transactions Failed,{transactions['failed']}\n")
            f.write(f"Transaction Success Rate,{transactions['successRate']}%\n\n")
            
            # Add detailed transaction information if available
            if "transactionResults" in raw_results:
                f.write("TRANSACTION RESULTS BY TYPE\n")
                f.write("Transaction Type,Attempted,Successful,Failed,Success Rate\n")
                
                for tx_type, tx_data in raw_results["transactionResults"].items():
                    attempted = tx_data.get("attempted", 0)
                    successful = tx_data.get("successful", 0)
                    failed = tx_data.get("failed", 0)
                    success_rate = 0
                    if attempted > 0:
                        success_rate = (successful / attempted) * 100
                    
                    # Escape any commas in the type to avoid CSV format issues
                    tx_type_esc = f'"{tx_type}"' if "," in tx_type else tx_type
                    
                    f.write(f"{tx_type_esc},{attempted},{successful},{failed},{success_rate:.2f}%\n")

class ComplianceReportGenerator(ReportGenerator):
    """Generates compliance-focused reports for test results"""
    
    def generate(self, summary: TestSummary, raw_results: Dict[str, Any], 
                output_format: str, output_file: str) -> str:
        """Generate a compliance report
        
        Args:
            summary: Test summary data
            raw_results: Raw test results
            output_format: Output format (html, csv, pdf)
            output_file: Path to output file
            
        Returns:
            str: Path to generated report
        """
        if output_format == "html":
            return self._generate_html(summary, raw_results, output_file)
        elif output_format == "csv":
            return self._generate_csv(summary, raw_results, output_file)
        else:
            raise ValueError(f"Unsupported output format: {output_format}")
    
    def _generate_html(self, summary: TestSummary, raw_results: Dict[str, Any], output_file: str) -> str:
        """Generate an HTML compliance report
        
        Args:
            summary: Test summary data
            raw_results: Raw test results
            output_file: Path to output file
            
        Returns:
            str: Path to generated report
        """
        with open(output_file, "w") as f:
            # Write HTML header with compliance-focused styling
            f.write(f"""
            <html>
            <head>
                <title>Compliance Report: {summary['testName']}</title>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 20px; color: #333; }}
                    h1 {{ color: #003366; }}
                    h2 {{ color: #003366; margin-top: 30px; }}
                    h3 {{ color: #003366; }}
                    .section {{ margin-bottom: 20px; padding: 15px; border: 1px solid #ddd; }}
                    .header {{ background-color: #f5f5f5; padding: 15px; border-bottom: 2px solid #003366; }}
                    .summary {{ font-size: 1.1em; margin: 15px 0; }}
                    .pass {{ background-color: #dff0d8; color: #3c763d; padding: 5px; }}
                    .fail {{ background-color: #f2dede; color: #a94442; padding: 5px; }}
                    .warning {{ background-color: #fcf8e3; color: #8a6d3b; padding: 5px; }}
                    table {{ border-collapse: collapse; width: 100%; margin-bottom: 20px; }}
                    th, td {{ padding: 8px; text-align: left; border: 1px solid #ddd; }}
                    th {{ background-color: #f2f2f2; }}
                    .footer {{ margin-top: 30px; font-size: 0.8em; color: #666; text-align: center; }}
                </style>
            </head>
            <body>
                <div class="header">
                    <h1>Compliance Report: {summary['testName']}</h1>
                    <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                </div>
            """)
            
            # Test Information section
            f.write('<h2>Test Information</h2><div class="section">')
            f.write("<table>")
            f.write("<tr><th>Parameter</th><th>Value</th></tr>")
            f.write(f"<tr><td>Test Name</td><td>{summary['testName']}</td></tr>")
            f.write(f"<tr><td>Test ID</td><td>{summary['testId']}</td></tr>")
            f.write(f"<tr><td>Run ID</td><td>{summary['runId']}</td></tr>")
            f.write(f"<tr><td>Test Type</td><td>{summary['testType']}</td></tr>")
            f.write(f"<tr><td>Start Time</td><td>{summary['startTime']}</td></tr>")
            f.write(f"<tr><td>End Time</td><td>{summary['endTime']}</td></tr>")
            f.write(f"<tr><td>Duration</td><td>{summary['duration']} seconds</td></tr>")
            f.write(f"<tr><td>Status</td><td>{summary['status']}</td></tr>")
            f.write("</table></div>")
            
            # Compliance Assessment section
            f.write('<h2>Compliance Assessment</h2><div class="section">')
            
            # Different compliance assessments based on test type
            if summary["testType"] == "strike":
                self._add_security_compliance(f, summary, raw_results)
            elif summary["testType"] in ["appsim", "clientsim"]:
                self._add_performance_compliance(f, summary, raw_results)
            else:
                f.write("<p>No compliance assessment available for this test type.</p>")
                
            f.write('</div>')
            
            # Recommendations section
            f.write('<h2>Recommendations</h2><div class="section">')
            
            # Generate recommendations based on test results
            if summary["testType"] == "strike":
                strikes = summary["metrics"].get("strikes", {})
                success_rate = strikes.get("successRate", 0)
                
                if success_rate >= 95:
                    f.write("<p>The security system is performing well against tested threats. Recommended actions:</p>")
                    f.write("<ul>")
                    f.write("<li>Maintain current security configurations</li>")
                    f.write("<li>Continue regular security testing to ensure ongoing compliance</li>")
                    f.write("<li>Document testing results for compliance audits</li>")
                    f.write("</ul>")
                elif success_rate >= 80:
                    f.write("<p>The security system shows adequate protection but has room for improvement. Recommended actions:</p>")
                    f.write("<ul>")
                    f.write("<li>Review security configurations for areas of improvement</li>")
                    f.write("<li>Analyze allowed strikes and implement mitigations</li>")
                    f.write("<li>Schedule follow-up testing after implementing changes</li>")
                    f.write("</ul>")
                else:
                    f.write("<p>The security system requires significant improvements to meet compliance requirements. Recommended actions:</p>")
                    f.write("<ul>")
                    f.write("<li>Immediate review of security configurations and policies</li>")
                    f.write("<li>Implement necessary security controls to address identified vulnerabilities</li>")
                    f.write("<li>Conduct remediation testing to verify improvements</li>")
                    f.write("<li>Consider security architecture review</li>")
                    f.write("</ul>")
            elif summary["testType"] in ["appsim", "clientsim"]:
                transactions = summary["metrics"].get("transactions", {})
                success_rate = transactions.get("successRate", 0)
                
                if success_rate >= 95:
                    f.write("<p>The application is performing well under test conditions. Recommended actions:</p>")
                    f.write("<ul>")
                    f.write("<li>Document performance metrics for compliance requirements</li>")
                    f.write("<li>Maintain current configuration and capacity</li>")
                    f.write("<li>Continue periodic performance testing to ensure ongoing compliance</li>")
                    f.write("</ul>")
                elif success_rate >= 80:
                    f.write("<p>The application shows adequate performance but has room for improvement. Recommended actions:</p>")
                    f.write("<ul>")
                    f.write("<li>Analyze failed transactions to identify performance bottlenecks</li>")
                    f.write("<li>Implement performance optimizations where needed</li>")
                    f.write("<li>Consider capacity increases if throughput is insufficient</li>")
                    f.write("<li>Schedule follow-up testing after implementing changes</li>")
                    f.write("</ul>")
                else:
                    f.write("<p>The application requires significant improvements to meet performance requirements. Recommended actions:</p>")
                    f.write("<ul>")
                    f.write("<li>Immediate investigation of performance issues</li>")
                    f.write("<li>Review application architecture and configuration</li>")
                    f.write("<li>Implement necessary optimizations and fixes</li>")
                    f.write("<li>Consider load balancing or capacity increases</li>")
                    f.write("<li>Conduct remediation testing to verify improvements</li>")
                    f.write("</ul>")
            
            f.write('</div>')
            
            # Footer with compliance statement
            f.write("""
                <div class="footer">
                    <p>This report is provided for compliance assessment purposes.</p>
                    <p>Generated by Breaking Point MCP Agent</p>
                </div>
            </body>
            </html>
            """)
            
        return output_file
    
    def _add_security_compliance(self, f: TextIO, summary: TestSummary, raw_results: Dict[str, Any]) -> None:
        """Add security compliance assessment
        
        Args:
            f: File object to write to
            summary: Test summary data
            raw_results: Raw test results
        """
        if "strikes" in summary["metrics"]:
            strikes = summary["metrics"]["strikes"]
            success_rate = strikes["successRate"]
            
            f.write("<h3>Security Control Effectiveness</h3>")
            f.write("<table>")
            f.write("<tr><th>Metric</th><th>Value</th><th>Threshold</th><th>Status</th></tr>")
            
            # Evaluate against common compliance thresholds
            status_class = "pass" if success_rate >= 95 else "warning" if success_rate >= 80 else "fail"
            status_text = "Pass" if success_rate >= 95 else "Warning" if success_rate >= 80 else "Fail"
            
            f.write(f"<tr><td>Protection Success Rate</td><td>{success_rate}%</td><td>95%</td>")
            f.write(f"<td class='{status_class}'>{status_text}</td></tr>")
            
            f.write(f"<tr><td>Strikes Blocked</td><td>{strikes['blocked']}</td><td>N/A</td><td>Informational</td></tr>")
            f.write(f"<tr><td>Strikes Allowed</td><td>{strikes['allowed']}</td><td>N/A</td><td>Informational</td></tr>")
            f.write("</table>")
            
            # Add compliance frameworks assessment
            f.write("<h3>Compliance Frameworks Assessment</h3>")
            f.write("<table>")
            f.write("<tr><th>Framework</th><th>Requirement</th><th>Status</th><th>Notes</th></tr>")
            
            # Example frameworks and requirements
            frameworks = [
                {
                    "name": "NIST SP 800-53",
                    "requirement": "SI-3 Malicious Code Protection",
                    "threshold": 90,
                    "notes": "Controls must effectively detect and prevent malicious code execution"
                },
                {
                    "name": "ISO 27001",
                    "requirement": "A.12.2.1 Controls against malware",
                    "threshold": 85,
                    "notes": "Detection, prevention and recovery controls to protect against malware"
                },
                {
                    "name": "PCI DSS",
                    "requirement": "Req. 5: Use and maintain anti-virus",
                    "threshold": 95,
                    "notes": "Systems must be protected from malicious software"
                }
            ]
            
            for fw in frameworks:
                status_class = "pass" if success_rate >= fw["threshold"] else "fail"
                status_text = "Pass" if success_rate >= fw["threshold"] else "Fail"
                
                f.write(f"<tr><td>{fw['name']}</td><td>{fw['requirement']}</td>")
                f.write(f"<td class='{status_class}'>{status_text}</td><td>{fw['notes']}</td></tr>")
                
            f.write("</table>")
            
            # Add detailed vulnerability assessment if available
            if "complianceDetails" in raw_results:
                f.write("<h3>Detailed Vulnerability Assessment</h3>")
                f.write("<table>")
                f.write("<tr><th>Vulnerability Category</th><th>Blocked</th><th>Allowed</th><th>Success Rate</th><th>Status</th></tr>")
                
                for category, details in raw_results["complianceDetails"].items():
                    cat_blocked = details.get("blocked", 0)
                    cat_allowed = details.get("allowed", 0)
                    cat_total = cat_blocked + cat_allowed
                    cat_rate = 0 if cat_total == 0 else (cat_blocked / cat_total) * 100
                    
                    status_class = "pass" if cat_rate >= 95 else "warning" if cat_rate >= 80 else "fail"
                    status_text = "Pass" if cat_rate >= 95 else "Warning" if cat_rate >= 80 else "Fail"
                    
                    f.write(f"<tr><td>{category}</td><td>{cat_blocked}</td><td>{cat_allowed}</td>")
                    f.write(f"<td>{cat_rate:.2f}%</td><td class='{status_class}'>{status_text}</td></tr>")
                    
                f.write("</table>")
    
    def _add_performance_compliance(self, f: TextIO, summary: TestSummary, raw_results: Dict[str, Any]) -> None:
        """Add performance compliance assessment
        
        Args:
            f: File object to write to
            summary: Test summary data
            raw_results: Raw test results
        """
        # Transaction success rate assessment
        if "transactions" in summary["metrics"]:
            transactions = summary["metrics"]["transactions"]
            success_rate = transactions["successRate"]
            
            f.write("<h3>Service Level Agreement Assessment</h3>")
            f.write("<table>")
            f.write("<tr><th>Metric</th><th>Value</th><th>SLA Target</th><th>Status</th></tr>")
            
            # Evaluate transaction success rate against SLA
            status_class = "pass" if success_rate >= 95 else "warning" if success_rate >= 90 else "fail"
            status_text = "Pass" if success_rate >= 95 else "Warning" if success_rate >= 90 else "Fail"
            
            f.write(f"<tr><td>Transaction Success Rate</td><td>{success_rate}%</td><td>95%</td>")
            f.write(f"<td class='{status_class}'>{status_text}</td></tr>")
            
            # Evaluate latency against SLA if available
            if "latency" in summary["metrics"]:
                latency = summary["metrics"]["latency"]
                # Example threshold: 100ms for average latency
                latency_threshold = 100
                avg_latency = latency["average"]
                latency_unit = latency["unit"]
                
                latency_status_class = "pass" if avg_latency <= latency_threshold else "fail"
                latency_status_text = "Pass" if avg_latency <= latency_threshold else "Fail"
                
                f.write(f"<tr><td>Average Latency</td><td>{avg_latency} {latency_unit}</td><td>≤ {latency_threshold} {latency_unit}</td>")
                f.write(f"<td class='{latency_status_class}'>{latency_status_text}</td></tr>")
            
            # Evaluate throughput against SLA if available
            if "throughput" in summary["metrics"]:
                throughput = summary["metrics"]["throughput"]
                # Example threshold: 500 mbps minimum throughput
                throughput_threshold = 500
                avg_throughput = throughput["average"]
                throughput_unit = throughput["unit"]
                
                throughput_status_class = "pass" if avg_throughput >= throughput_threshold else "fail"
                throughput_status_text = "Pass" if avg_throughput >= throughput_threshold else "Fail"
                
                f.write(f"<tr><td>Average Throughput</td><td>{avg_throughput} {throughput_unit}</td><td>≥ {throughput_threshold} {throughput_unit}</td>")
                f.write(f"<td class='{throughput_status_class}'>{throughput_status_text}</td></tr>")
                
            f.write("</table>")
            
            # Compliance frameworks for performance
            f.write("<h3>Performance Requirements Assessment</h3>")
            f.write("<table>")
            f.write("<tr><th>Standard/Framework</th><th>Requirement</th><th>Status</th><th>Notes</th></tr>")
            
            # Example frameworks and requirements for performance
            frameworks = [
                {
                    "name": "Internal SLA",
                    "requirement": "Transaction Success Rate >= 95%",
                    "threshold": 95,
                    "notes": "Business critical applications must maintain high success rates",
                    "metric": success_rate
                },
            ]
            
            # Add latency requirement if available
            if "latency" in summary["metrics"]:
                frameworks.append({
                    "name": "Internal SLA",
                    "requirement": f"Average Latency <= {latency_threshold} ms",
                    "threshold": latency_threshold,
                    "notes": "Response times must meet user experience requirements",
                    "metric": avg_latency,
                    "compare": "less"  # Compare less than threshold
                })
            
            # Add throughput requirement if available
            if "throughput" in summary["metrics"]:
                frameworks.append({
                    "name": "Capacity Plan",
                    "requirement": f"Throughput >= {throughput_threshold} mbps",
                    "threshold": throughput_threshold,
                    "notes": "Must support minimum throughput requirements",
                    "metric": avg_throughput,
                    "compare": "greater"  # Compare greater than threshold
                })
            
            for fw in frameworks:
                # Determine status based on comparison type
                if fw.get("compare") == "less":
                    # For metrics where lower is better (like latency)
                    status_class = "pass" if fw["metric"] <= fw["threshold"] else "fail"
                    status_text = "Pass" if fw["metric"] <= fw["threshold"] else "Fail"
                elif fw.get("compare") == "greater":
                    # For metrics where higher is better (like throughput)
                    status_class = "pass" if fw["metric"] >= fw["threshold"] else "fail"
                    status_text = "Pass" if fw["metric"] >= fw["threshold"] else "Fail"
                else:
                    # Default comparison (percentage metrics like success rate)
                    status_class = "pass" if fw["metric"] >= fw["threshold"] else "fail"
                    status_text = "Pass" if fw["metric"] >= fw["threshold"] else "Fail"
                
                f.write(f"<tr><td>{fw['name']}</td><td>{fw['requirement']}</td>")
                f.write(f"<td class='{status_class}'>{status_text}</td><td>{fw['notes']}</td></tr>")
                
            f.write("</table>")
    
    def _generate_csv(self, summary: TestSummary, raw_results: Dict[str, Any], output_file: str) -> str:
        """Generate a CSV compliance report
        
        Args:
            summary: Test summary data
            raw_results: Raw test results
            output_file: Path to output file
            
        Returns:
            str: Path to generated report
        """
        with open(output_file, "w") as f:
            f.write(f"Test Name,{summary['testName']}\n")
            f.write(f"Report Type,Compliance Report\n")
            f.write(f"Generated,{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            # Test Information
            f.write("TEST INFORMATION\n")
            f.write(f"Test ID,{summary['testId']}\n")
            f.write(f"Run ID,{summary['runId']}\n")
            f.write(f"Test Type,{summary['testType']}\n")
            f.write(f"Start Time,{summary['startTime']}\n")
            f.write(f"End Time,{summary['endTime']}\n")
            f.write(f"Duration,{summary['duration']} seconds\n")
            f.write(f"Status,{summary['status']}\n\n")
            
            # Compliance Assessment section
            f.write("COMPLIANCE ASSESSMENT\n")
            
            # Different compliance assessments based on test type
            if summary["testType"] == "strike":
                self._write_csv_security_compliance(f, summary, raw_results)
            elif summary["testType"] in ["appsim", "clientsim"]:
                self._write_csv_performance_compliance(f, summary, raw_results)
            else:
                f.write("No compliance assessment available for this test type.\n\n")
            
            # Recommendations section
            f.write("RECOMMENDATIONS\n")
            
            # Generate recommendations based on test results
            if summary["testType"] == "strike":
                strikes = summary["metrics"].get("strikes", {})
                success_rate = strikes.get("successRate", 0)
                
                if success_rate >= 95:
                    f.write("The security system is performing well against tested threats. Recommended actions:\n")
                    f.write("1. Maintain current security configurations\n")
                    f.write("2. Continue regular security testing to ensure ongoing compliance\n")
                    f.write("3. Document testing results for compliance audits\n\n")
                elif success_rate >= 80:
                    f.write("The security system shows adequate protection but has room for improvement. Recommended actions:\n")
                    f.write("1. Review security configurations for areas of improvement\n")
                    f.write("2. Analyze allowed strikes and implement mitigations\n")
                    f.write("3. Schedule follow-up testing after implementing changes\n\n")
                else:
                    f.write("The security system requires significant improvements to meet compliance requirements. Recommended actions:\n")
                    f.write("1. Immediate review of security configurations and policies\n")
                    f.write("2. Implement necessary security controls to address identified vulnerabilities\n")
                    f.write("3. Conduct remediation testing to verify improvements\n")
                    f.write("4. Consider security architecture review\n\n")
            elif summary["testType"] in ["appsim", "clientsim"]:
                transactions = summary["metrics"].get("transactions", {})
                success_rate = transactions.get("successRate", 0)
                
                if success_rate >= 95:
                    f.write("The application is performing well under test conditions. Recommended actions:\n")
                    f.write("1. Document performance metrics for compliance requirements\n")
                    f.write("2. Maintain current configuration and capacity\n")
                    f.write("3. Continue periodic performance testing to ensure ongoing compliance\n\n")
                elif success_rate >= 80:
                    f.write("The application shows adequate performance but has room for improvement. Recommended actions:\n")
                    f.write("1. Analyze failed transactions to identify performance bottlenecks\n")
                    f.write("2. Implement performance optimizations where needed\n")
                    f.write("3. Consider capacity increases if throughput is insufficient\n")
                    f.write("4. Schedule follow-up testing after implementing changes\n\n")
                else:
                    f.write("The application requires significant improvements to meet performance requirements. Recommended actions:\n")
                    f.write("1. Immediate investigation of performance issues\n")
                    f.write("2. Review application architecture and configuration\n")
                    f.write("3. Implement necessary optimizations and fixes\n")
                    f.write("4. Consider load balancing or capacity increases\n")
                    f.write("5. Conduct remediation testing to verify improvements\n\n")
            
            # Footer
            f.write("This report is provided for compliance assessment purposes.\n")
            f.write("Generated by Breaking Point MCP Agent\n")
                
        return output_file
    
    def _write_csv_security_compliance(self, f: TextIO, summary: TestSummary, raw_results: Dict[str, Any]) -> None:
        """Write security compliance assessment to CSV
        
        Args:
            f: File object to write to
            summary: Test summary data
            raw_results: Raw test results
        """
        if "strikes" in summary["metrics"]:
            strikes = summary["metrics"]["strikes"]
            success_rate = strikes["successRate"]
            
            f.write("Security Control Effectiveness\n")
            f.write("Metric,Value,Threshold,Status\n")
            
            # Evaluate against common compliance thresholds
            status_text = "Pass" if success_rate >= 95 else "Warning" if success_rate >= 80 else "Fail"
            
            f.write(f"Protection Success Rate,{success_rate}%,95%,{status_text}\n")
            f.write(f"Strikes Blocked,{strikes['blocked']},N/A,Informational\n")
            f.write(f"Strikes Allowed,{strikes['allowed']},N/A,Informational\n\n")
            
            # Add compliance frameworks assessment
            f.write("Compliance Frameworks Assessment\n")
            f.write("Framework,Requirement,Status,Notes\n")
            
            # Example frameworks and requirements
            frameworks = [
                {
                    "name": "NIST SP 800-53",
                    "requirement": "SI-3 Malicious Code Protection",
                    "threshold": 90,
                    "notes": "Controls must effectively detect and prevent malicious code execution"
                },
                {
                    "name": "ISO 27001",
                    "requirement": "A.12.2.1 Controls against malware",
                    "threshold": 85,
                    "notes": "Detection, prevention and recovery controls to protect against malware"
                },
                {
                    "name": "PCI DSS",
                    "requirement": "Req. 5: Use and maintain anti-virus",
                    "threshold": 95,
                    "notes": "Systems must be protected from malicious software"
                }
            ]
            
            for fw in frameworks:
                status_text = "Pass" if success_rate >= fw["threshold"] else "Fail"
                
                # Escape any commas in the fields
                requirement = f'"{fw["requirement"]}"' if "," in fw["requirement"] else fw["requirement"]
                notes = f'"{fw["notes"]}"' if "," in fw["notes"] else fw["notes"]
                
                f.write(f"{fw['name']},{requirement},{status_text},{notes}\n")
                
            f.write("\n")
    
    def _write_csv_performance_compliance(self, f: TextIO, summary: TestSummary, raw_results: Dict[str, Any]) -> None:
        """Write performance compliance assessment to CSV
        
        Args:
            f: File object to write to
            summary: Test summary data
            raw_results: Raw test results
        """
        # Transaction success rate assessment
        if "transactions" in summary["metrics"]:
            transactions = summary["metrics"]["transactions"]
            success_rate = transactions["successRate"]
            
            f.write("Service Level Agreement Assessment\n")
            f.write("Metric,Value,SLA Target,Status\n")
            
            # Evaluate transaction success rate against SLA
            status_text = "Pass" if success_rate >= 95 else "Warning" if success_rate >= 90 else "Fail"
            
            f.write(f"Transaction Success Rate,{success_rate}%,95%,{status_text}\n")
            
            # Evaluate latency against SLA if available
            if "latency" in summary["metrics"]:
                latency = summary["metrics"]["latency"]
                # Example threshold: 100ms for average latency
                latency_threshold = 100
                avg_latency = latency["average"]
                latency_unit = latency["unit"]
                
                latency_status_text = "Pass" if avg_latency <= latency_threshold else "Fail"
                
                f.write(f"Average Latency,{avg_latency} {latency_unit},≤ {latency_threshold} {latency_unit},{latency_status_text}\n")
            
            # Evaluate throughput against SLA if available
            if "throughput" in summary["metrics"]:
                throughput = summary["metrics"]["throughput"]
                # Example threshold: 500 mbps minimum throughput
                throughput_threshold = 500
                avg_throughput = throughput["average"]
                throughput_unit = throughput["unit"]
                
                throughput_status_text = "Pass" if avg_throughput >= throughput_threshold else "Fail"
                
                f.write(f"Average Throughput,{avg_throughput} {throughput_unit},≥ {throughput_threshold} {throughput_unit},{throughput_status_text}\n")
                
            f.write("\n")
