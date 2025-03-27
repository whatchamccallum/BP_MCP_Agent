"""
Compliance report generator module
"""

from datetime import datetime
from typing import Dict, TextIO, Any

def generate_compliance_report(file: TextIO, summary: Dict[str, Any], raw_results: Dict[str, Any]):
    """Generate a compliance-focused HTML report
    
    Args:
        file: File object to write to
        summary: Test result summary
        raw_results: Raw test results
    """
    # Compliance Overview section
    file.write("""
        <div class="section">
            <h2>Compliance Assessment Overview</h2>
    """)
    
    # For security tests, focus on compliance metrics
    if "strikes" in summary["metrics"]:
        strikes = summary["metrics"]["strikes"]
        success_rate = strikes["successRate"]
        
        # Determine compliance status
        compliance_status = "Compliant" if success_rate >= 95 else "Non-Compliant"
        status_class = "pass" if compliance_status == "Compliant" else "fail"
        
        file.write(f"""
            <p class="summary">Compliance Status: <span class="{status_class}">{compliance_status}</span></p>
            <p>Security Protection Level: {success_rate}%</p>
            <p>Assessment Date: {datetime.now().strftime('%Y-%m-%d')}</p>
            
            <h3>Compliance Metrics</h3>
            <table>
                <tr><th>Metric</th><th>Value</th><th>Threshold</th><th>Status</th></tr>
                <tr>
                    <td>Attack Blocking Rate</td>
                    <td>{success_rate}%</td>
                    <td>95%</td>
                    <td class="{status_class}">{compliance_status}</td>
                </tr>
        """)
        
        # Add specific compliance checks if available in raw results
        if raw_results and "complianceChecks" in raw_results:
            for check in raw_results["complianceChecks"]:
                check_status = "Compliant" if check.get("passed", False) else "Non-Compliant"
                check_class = "pass" if check_status == "Compliant" else "fail"
                
                file.write(f"""
                <tr>
                    <td>{check.get('name', 'Unknown Check')}</td>
                    <td>{check.get('value', 'N/A')}</td>
                    <td>{check.get('threshold', 'N/A')}</td>
                    <td class="{check_class}">{check_status}</td>
                </tr>
                """)
                
        file.write("""
            </table>
        </div>
        """)
        
        # Add Compliance Standards section
        file.write("""
        <div class="section">
            <h2>Compliance Standards</h2>
            <table>
                <tr><th>Standard</th><th>Requirement</th><th>Status</th></tr>
        """)
        
        # Add standard compliance mappings
        compliance_standards = [
            {"standard": "PCI-DSS", "requirement": "11.2 - Vulnerability Scanning", "compliant": success_rate >= 95},
            {"standard": "NIST SP 800-53", "requirement": "RA-5 - Vulnerability Scanning", "compliant": success_rate >= 90},
            {"standard": "ISO 27001", "requirement": "A.12.6.1 - Technical Vulnerability Management", "compliant": success_rate >= 90}
        ]
        
        for std in compliance_standards:
            status = "Compliant" if std["compliant"] else "Non-Compliant"
            status_class = "pass" if std["compliant"] else "fail"
            
            file.write(f"""
            <tr>
                <td>{std["standard"]}</td>
                <td>{std["requirement"]}</td>
                <td class="{status_class}">{status}</td>
            </tr>
            """)
            
        file.write("""
            </table>
        </div>
        """)
        
        # Remediation section for non-compliant findings
        if compliance_status == "Non-Compliant":
            file.write("""
            <div class="section">
                <h2>Remediation Plan</h2>
                <p>The following remediation steps are recommended to achieve compliance:</p>
                <ol>
                    <li>Review all failed security tests and identify patterns in the allowed attacks</li>
                    <li>Update security policies and rules to address identified vulnerabilities</li>
                    <li>Implement additional security controls as needed</li>
                    <li>Conduct a follow-up security assessment to verify remediation effectiveness</li>
                    <li>Document all changes and maintain evidence for compliance audits</li>
                </ol>
            </div>
            """)
    else:
        # For non-security tests, provide a general performance compliance section
        file.write("""
            <p>This test type does not directly map to security compliance standards.</p>
            <p>For compliance assessment, please run a security-focused test.</p>
        </div>
        """)
