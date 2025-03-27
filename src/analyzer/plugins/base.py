"""
Plugin interface definitions for analyzer extensions.
"""
from abc import ABC, abstractmethod
import io
from typing import Dict, List, Any, Optional, Protocol, TextIO, TypedDict, Union, Literal

class MetricData(TypedDict):
    """Type definition for metric data"""
    average: float
    maximum: float
    unit: str

class StrikeMetrics(TypedDict):
    """Type definition for strike metrics"""
    attempted: int
    blocked: int
    allowed: int
    successRate: float

class TransactionMetrics(TypedDict):
    """Type definition for transaction metrics"""
    attempted: int
    successful: int
    failed: int
    successRate: float

class TestMetrics(TypedDict, total=False):
    """Type definition for test metrics"""
    throughput: MetricData
    latency: MetricData
    strikes: StrikeMetrics
    transactions: TransactionMetrics

class TestSummary(TypedDict):
    """Type definition for test summary"""
    testId: str
    runId: str
    testName: str
    testType: str
    startTime: str
    endTime: str
    duration: float
    status: str
    metrics: TestMetrics

class ReportGenerator(ABC):
    """Base class for report generators"""
    
    @abstractmethod
    def generate(self, summary: TestSummary, raw_results: Dict[str, Any], 
                output_format: str, output_file: str) -> str:
        """Generate a report from test results
        
        Args:
            summary: Test summary data
            raw_results: Raw test results
            output_format: Output format (html, csv, pdf)
            output_file: Path to output file
            
        Returns:
            str: Path to generated report
        """
        pass
    
    def write_html_section(self, f: TextIO, title: str, content: Union[str, Dict, List]) -> None:
        """Write a section to an HTML report
        
        Args:
            f: File-like object to write to
            title: Section title
            content: Section content
        """
        f.write(f"<h2>{title}</h2>\n<div class='section'>\n")
        
        if isinstance(content, str):
            f.write(f"<p>{content}</p>\n")
        elif isinstance(content, dict):
            f.write("<table>\n")
            for key, value in content.items():
                f.write(f"<tr><th>{key}</th><td>{value}</td></tr>\n")
            f.write("</table>\n")
        elif isinstance(content, list):
            f.write("<ul>\n")
            for item in content:
                f.write(f"<li>{item}</li>\n")
            f.write("</ul>\n")
                
        f.write("</div>\n")

class ChartGenerator(ABC):
    """Base class for chart generators"""
    
    @abstractmethod
    def generate(self, summary: TestSummary, raw_results: Dict[str, Any], 
                output_file: str) -> str:
        """Generate a chart from test results
        
        Args:
            summary: Test summary data
            raw_results: Raw test results
            output_file: Path to output file
            
        Returns:
            str: Path to generated chart
        """
        pass

class AnalyzerPlugin(ABC):
    """Base class for analyzer plugins"""
    
    @abstractmethod
    def analyze(self, raw_results: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze test results
        
        Args:
            raw_results: Raw test results
            
        Returns:
            Dict[str, Any]: Analysis results
        """
        pass
    
    @abstractmethod
    def get_summary(self, raw_results: Dict[str, Any]) -> Dict[str, Any]:
        """Get a summary of test results
        
        Args:
            raw_results: Raw test results
            
        Returns:
            Dict[str, Any]: Summary results
        """
        pass

class PluginManager:
    """Manages analyzer plugins"""
    
    def __init__(self):
        self.report_generators: Dict[str, ReportGenerator] = {}
        self.chart_generators: Dict[str, ChartGenerator] = {}
        self.analyzers: Dict[str, AnalyzerPlugin] = {}
    
    def register_report_generator(self, name: str, generator: ReportGenerator) -> None:
        """Register a report generator plugin
        
        Args:
            name: Plugin name
            generator: Report generator instance
        """
        self.report_generators[name] = generator
    
    def register_chart_generator(self, name: str, generator: ChartGenerator) -> None:
        """Register a chart generator plugin
        
        Args:
            name: Plugin name
            generator: Chart generator instance
        """
        self.chart_generators[name] = generator
    
    def register_analyzer(self, name: str, analyzer: AnalyzerPlugin) -> None:
        """Register an analyzer plugin
        
        Args:
            name: Plugin name
            analyzer: Analyzer instance
        """
        self.analyzers[name] = analyzer
    
    def get_report_generator(self, name: str) -> Optional[ReportGenerator]:
        """Get a report generator by name
        
        Args:
            name: Generator name
            
        Returns:
            Optional[ReportGenerator]: Report generator or None if not found
        """
        return self.report_generators.get(name)
    
    def get_chart_generator(self, name: str) -> Optional[ChartGenerator]:
        """Get a chart generator by name
        
        Args:
            name: Generator name
            
        Returns:
            Optional[ChartGenerator]: Chart generator or None if not found
        """
        return self.chart_generators.get(name)
    
    def get_analyzer(self, name: str) -> Optional[AnalyzerPlugin]:
        """Get an analyzer by name
        
        Args:
            name: Analyzer name
            
        Returns:
            Optional[AnalyzerPlugin]: Analyzer or None if not found
        """
        return self.analyzers.get(name)
