"""
Report generator module for test result analysis
"""

from .standard import generate_standard_report
from .executive import generate_executive_report
from .detailed import generate_detailed_report, generate_detailed_security_section, generate_detailed_performance_section
from .compliance import generate_compliance_report
