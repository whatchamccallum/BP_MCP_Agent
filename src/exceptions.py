"""
Exception classes for the Breaking Point MCP Agent
This module defines custom exceptions for better error handling.
"""
from typing import Optional, Dict, Any, List

class BPError(Exception):
    """Base class for all Breaking Point MCP Agent exceptions"""
    
    def __init__(self, message: str, error_code: Optional[str] = None, 
                retry_possible: bool = False, details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.error_code = error_code
        self.retry_possible = retry_possible
        self.details = details or {}
        super().__init__(message)
    
    def __str__(self) -> str:
        """Format the exception message"""
        if self.error_code:
            return f"[{self.error_code}] {self.message}"
        return self.message
    
    def get_user_message(self) -> str:
        """Get a user-friendly error message"""
        return self.message

class APIError(BPError):
    """Raised when an API call fails"""
    
    def __init__(self, message: str, status_code: Optional[int] = None, 
                response: Optional[str] = None, endpoint: Optional[str] = None,
                retry_possible: bool = False, error_code: Optional[str] = None):
        self.status_code = status_code
        self.response = response
        self.endpoint = endpoint
        details = {
            "status_code": status_code,
            "endpoint": endpoint
        }
        if response:
            details["response"] = response
            
        super().__init__(message, error_code=error_code or "API_ERROR", 
                        retry_possible=retry_possible, details=details)
    
    def get_user_message(self) -> str:
        """Get a user-friendly error message"""
        if self.endpoint and self.status_code:
            return f"API request to '{self.endpoint}' failed with status {self.status_code}: {self.message}"
        return f"API request failed: {self.message}"

class AuthenticationError(APIError):
    """Raised when authentication fails"""
    
    def __init__(self, message: str, status_code: Optional[int] = None, 
                response: Optional[str] = None, endpoint: Optional[str] = None):
        super().__init__(message, status_code, response, endpoint, 
                        retry_possible=False, error_code="AUTH_ERROR")
    
    def get_user_message(self) -> str:
        """Get a user-friendly error message"""
        return f"Authentication failed: {self.message}. Please check your credentials."

class NetworkError(APIError):
    """Raised when a network connection error occurs"""
    
    def __init__(self, message: str, endpoint: Optional[str] = None, 
                is_timeout: bool = False, retry_count: int = 0,
                max_retries: Optional[int] = None):
        self.is_timeout = is_timeout
        self.retry_count = retry_count
        self.max_retries = max_retries
        
        # Network errors are usually transient and can be retried
        retry_possible = retry_count < (max_retries or 3)
        
        details = {
            "endpoint": endpoint,
            "is_timeout": is_timeout,
            "retry_count": retry_count,
            "max_retries": max_retries
        }
        
        error_code = "TIMEOUT_ERROR" if is_timeout else "NETWORK_ERROR"
        super().__init__(message, None, None, endpoint, 
                        retry_possible=retry_possible, error_code=error_code)
    
    def get_user_message(self) -> str:
        """Get a user-friendly error message"""
        if self.is_timeout:
            msg = f"Connection timed out"
        else:
            msg = f"Network connection error"
            
        if self.endpoint:
            msg += f" while connecting to '{self.endpoint}'"
            
        if self.retry_count > 0:
            if self.max_retries and self.retry_count >= self.max_retries:
                msg += f". Failed after {self.retry_count} retries"
            else:
                msg += f". Retry {self.retry_count} failed"
                
        return f"{msg}: {self.message}"

class TestError(BPError):
    """Base class for test-related errors"""
    
    def __init__(self, message: str, test_id: Optional[str] = None, 
                run_id: Optional[str] = None, error_code: Optional[str] = None,
                retry_possible: bool = False, details: Optional[Dict[str, Any]] = None):
        self.test_id = test_id
        self.run_id = run_id
        
        _details = {
            "test_id": test_id,
            "run_id": run_id
        }
        if details:
            _details.update(details)
            
        super().__init__(message, error_code=error_code, 
                        retry_possible=retry_possible, details=_details)
    
    def get_user_message(self) -> str:
        """Get a user-friendly error message"""
        test_info = ""
        if self.test_id:
            test_info = f" for test '{self.test_id}'"
            if self.run_id:
                test_info += f", run '{self.run_id}'"
                
        return f"Test operation failed{test_info}: {self.message}"

class TestCreationError(TestError):
    """Raised when test creation fails"""
    
    def __init__(self, message: str, test_config: Optional[Dict[str, Any]] = None, 
                error_code: Optional[str] = None):
        details = {}
        if test_config:
            details["test_config"] = test_config
            
        super().__init__(message, error_code=error_code or "TEST_CREATION_ERROR", 
                        retry_possible=False, details=details)
    
    def get_user_message(self) -> str:
        """Get a user-friendly error message"""
        return f"Failed to create test: {self.message}"

class TestExecutionError(TestError):
    """Raised when test execution fails"""
    
    def __init__(self, message: str, test_id: str, run_id: Optional[str] = None,
                status: Optional[str] = None, error_code: Optional[str] = None,
                retry_possible: bool = False):
        details = {"status": status} if status else {}
        super().__init__(message, test_id, run_id, 
                        error_code=error_code or "TEST_EXECUTION_ERROR",
                        retry_possible=retry_possible, details=details)
    
    def get_user_message(self) -> str:
        """Get a user-friendly error message"""
        test_info = f"test '{self.test_id}'"
        if self.run_id:
            test_info += f", run '{self.run_id}'"
            
        status_info = ""
        if self.details.get("status"):
            status_info = f" (status: {self.details['status']})"
            
        return f"Failed to execute {test_info}{status_info}: {self.message}"

class TestResultError(TestError):
    """Raised when retrieving or processing test results fails"""
    
    def __init__(self, message: str, test_id: Optional[str] = None, 
                run_id: Optional[str] = None, error_code: Optional[str] = None,
                retry_possible: bool = False):
        super().__init__(message, test_id, run_id, 
                        error_code=error_code or "TEST_RESULT_ERROR",
                        retry_possible=retry_possible)
    
    def get_user_message(self) -> str:
        """Get a user-friendly error message"""
        test_info = ""
        if self.test_id:
            test_info = f" for test '{self.test_id}'"
            if self.run_id:
                test_info += f", run '{self.run_id}'"
                
        return f"Failed to retrieve test results{test_info}: {self.message}"

class ValidationError(BPError):
    """Raised when validation of input data fails"""
    
    def __init__(self, message: str, validation_errors: Optional[Dict[str, str]] = None,
                field_name: Optional[str] = None):
        self.validation_errors = validation_errors or {}
        self.field_name = field_name
        
        details = {
            "validation_errors": self.validation_errors,
            "field_name": field_name
        }
        
        super().__init__(message, error_code="VALIDATION_ERROR", 
                        retry_possible=False, details=details)
    
    def get_user_message(self) -> str:
        """Get a user-friendly error message"""
        if self.field_name:
            return f"Validation error for field '{self.field_name}': {self.message}"
        if self.validation_errors:
            # Format the validation errors
            error_list = [f"{field}: {error}" for field, error in self.validation_errors.items()]
            error_str = "; ".join(error_list)
            return f"Validation errors: {error_str}"
        return f"Validation error: {self.message}"

class ConfigurationError(BPError):
    """Raised when there's an issue with configuration"""
    
    def __init__(self, message: str, config_key: Optional[str] = None, 
                config_section: Optional[str] = None):
        self.config_key = config_key
        self.config_section = config_section
        
        details = {
            "config_key": config_key,
            "config_section": config_section
        }
        
        super().__init__(message, error_code="CONFIG_ERROR", 
                        retry_possible=False, details=details)
    
    def get_user_message(self) -> str:
        """Get a user-friendly error message"""
        if self.config_section and self.config_key:
            return f"Configuration error in section '{self.config_section}', key '{self.config_key}': {self.message}"
        elif self.config_section:
            return f"Configuration error in section '{self.config_section}': {self.message}"
        else:
            return f"Configuration error: {self.message}"

class ReportError(BPError):
    """Raised when report generation fails"""
    
    def __init__(self, message: str, report_type: Optional[str] = None,
                output_format: Optional[str] = None, test_id: Optional[str] = None,
                run_id: Optional[str] = None):
        self.report_type = report_type
        self.output_format = output_format
        
        details = {
            "report_type": report_type,
            "output_format": output_format,
            "test_id": test_id,
            "run_id": run_id
        }
        
        super().__init__(message, error_code="REPORT_ERROR", 
                        retry_possible=False, details=details)
    
    def get_user_message(self) -> str:
        """Get a user-friendly error message"""
        report_info = ""
        if self.report_type:
            report_info = f" {self.report_type}"
        if self.output_format:
            report_info += f" ({self.output_format})"
            
        test_info = ""
        if self.details.get("test_id"):
            test_info = f" for test '{self.details['test_id']}'"
            if self.details.get("run_id"):
                test_info += f", run '{self.details['run_id']}'"
                
        return f"Failed to generate{report_info} report{test_info}: {self.message}"

class ChartError(BPError):
    """Raised when chart generation fails"""
    
    def __init__(self, message: str, chart_type: Optional[str] = None,
                test_id: Optional[str] = None, run_id: Optional[str] = None):
        self.chart_type = chart_type
        
        details = {
            "chart_type": chart_type,
            "test_id": test_id,
            "run_id": run_id
        }
        
        super().__init__(message, error_code="CHART_ERROR", 
                        retry_possible=False, details=details)
    
    def get_user_message(self) -> str:
        """Get a user-friendly error message"""
        chart_info = ""
        if self.chart_type:
            chart_info = f" {self.chart_type}"
            
        test_info = ""
        if self.details.get("test_id"):
            test_info = f" for test '{self.details['test_id']}'"
            if self.details.get("run_id"):
                test_info += f", run '{self.details['run_id']}'"
                
        return f"Failed to generate{chart_info} chart{test_info}: {self.message}"

class ResourceNotFoundError(BPError):
    """Raised when a required resource is not found"""
    
    def __init__(self, resource_type: str, resource_id: str):
        self.resource_type = resource_type
        self.resource_id = resource_id
        
        details = {
            "resource_type": resource_type,
            "resource_id": resource_id
        }
        
        message = f"{resource_type} with ID '{resource_id}' not found"
        super().__init__(message, error_code="RESOURCE_NOT_FOUND", 
                        retry_possible=False, details=details)
    
    def get_user_message(self) -> str:
        """Get a user-friendly error message"""
        return f"Resource not found: {self.resource_type} with ID '{self.resource_id}'"

class CacheError(BPError):
    """Raised when a cache operation fails"""
    
    def __init__(self, message: str, operation: Optional[str] = None,
                test_id: Optional[str] = None, run_id: Optional[str] = None):
        self.operation = operation
        
        details = {
            "operation": operation,
            "test_id": test_id,
            "run_id": run_id
        }
        
        super().__init__(message, error_code="CACHE_ERROR", 
                        retry_possible=False, details=details)
    
    def get_user_message(self) -> str:
        """Get a user-friendly error message"""
        operation_info = ""
        if self.operation:
            operation_info = f" during {self.operation}"
            
        test_info = ""
        if self.details.get("test_id"):
            test_info = f" for test '{self.details['test_id']}'"
            if self.details.get("run_id"):
                test_info += f", run '{self.details['run_id']}'"
                
        return f"Cache error{operation_info}{test_info}: {self.message}"

class PluginError(BPError):
    """Raised when there's an issue with a plugin"""
    
    def __init__(self, message: str, plugin_type: Optional[str] = None,
                plugin_name: Optional[str] = None):
        self.plugin_type = plugin_type
        self.plugin_name = plugin_name
        
        details = {
            "plugin_type": plugin_type,
            "plugin_name": plugin_name
        }
        
        super().__init__(message, error_code="PLUGIN_ERROR", 
                        retry_possible=False, details=details)
    
    def get_user_message(self) -> str:
        """Get a user-friendly error message"""
        plugin_info = ""
        if self.plugin_type and self.plugin_name:
            plugin_info = f" with {self.plugin_type} plugin '{self.plugin_name}'"
        elif self.plugin_type:
            plugin_info = f" with {self.plugin_type} plugin"
        elif self.plugin_name:
            plugin_info = f" with plugin '{self.plugin_name}'"
            
        return f"Plugin error{plugin_info}: {self.message}"

class RetryableError(BPError):
    """Base class for errors that can be retried"""
    
    def __init__(self, message: str, retry_count: int = 0, max_retries: Optional[int] = None,
                error_code: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        self.retry_count = retry_count
        self.max_retries = max_retries
        
        _details = {
            "retry_count": retry_count,
            "max_retries": max_retries
        }
        if details:
            _details.update(details)
            
        # Retry is possible if we haven't reached max retries
        retry_possible = max_retries is None or retry_count < max_retries
        
        super().__init__(message, error_code=error_code, 
                        retry_possible=retry_possible, details=_details)
    
    def get_user_message(self) -> str:
        """Get a user-friendly error message"""
        retry_info = ""
        if self.retry_count > 0:
            if self.max_retries and self.retry_count >= self.max_retries:
                retry_info = f" after {self.retry_count} retries"
            else:
                retry_info = f" (retry {self.retry_count})"
                
        return f"Operation failed{retry_info}: {self.message}"

def format_error_for_user(error: Exception) -> str:
    """Format an exception into a user-friendly error message
    
    Args:
        error: The exception to format
        
    Returns:
        str: User-friendly error message
    """
    if isinstance(error, BPError):
        return error.get_user_message()
    else:
        return str(error)

def format_error_for_logging(error: Exception) -> str:
    """Format an exception for logging with additional context
    
    Args:
        error: The exception to format
        
    Returns:
        str: Detailed error message for logging
    """
    if isinstance(error, BPError):
        details_str = ", ".join(f"{k}={v}" for k, v in error.details.items() if v is not None)
        if details_str:
            return f"{error} [{details_str}]"
        return str(error)
    else:
        return str(error)

def _flatten_error_dict(error_dict: Dict[str, Any], parent_key: str = "") -> Dict[str, str]:
    """Flatten a nested error dictionary into a simple key-value dictionary
    
    Args:
        error_dict: Nested error dictionary
        parent_key: Parent key for nested dictionaries
        
    Returns:
        Dict[str, str]: Flattened error dictionary
    """
    items = []
    for k, v in error_dict.items():
        new_key = f"{parent_key}.{k}" if parent_key else k
        
        if isinstance(v, dict):
            items.extend(_flatten_error_dict(v, new_key).items())
        else:
            items.append((new_key, str(v)))
            
    return dict(items)

def build_validation_error(error_dict: Dict[str, Any]) -> ValidationError:
    """Build a validation error from a dictionary of validation errors
    
    Args:
        error_dict: Dictionary of validation errors
        
    Returns:
        ValidationError: Validation error object
    """
    flat_errors = _flatten_error_dict(error_dict)
    message = "; ".join(f"{k}: {v}" for k, v in flat_errors.items())
    return ValidationError(message, validation_errors=flat_errors)

class ErrorHandler:
    """Utility class for handling errors and retries"""
    
    @staticmethod
    def retry_with_backoff(func, max_retries: int = 3, base_delay: float = 1.0,
                          retry_exceptions: List[type] = None, 
                          logger=None) -> Any:
        """Execute a function with retry and exponential backoff
        
        Args:
            func: Function to execute
            max_retries: Maximum number of retries
            base_delay: Base delay between retries in seconds
            retry_exceptions: List of exceptions to retry on
            logger: Logger to use for logging retries
            
        Returns:
            Any: Result of the function
            
        Raises:
            Exception: The last exception raised
        """
        import time
        import random
        
        if retry_exceptions is None:
            # Default to retrying on network errors
            retry_exceptions = [NetworkError, RetryableError]
        
        last_exception = None
        
        for retry in range(max_retries + 1):
            try:
                return func()
            except tuple(retry_exceptions) as e:
                last_exception = e
                
                # Check if the error is retryable
                if hasattr(e, 'retry_possible') and not e.retry_possible:
                    # Not retryable, re-raise immediately
                    raise
                
                # If this was the last retry, re-raise the exception
                if retry >= max_retries:
                    if logger:
                        logger.error(f"Failed after {retry + 1} attempts: {format_error_for_logging(e)}")
                    raise
                
                # Calculate delay with exponential backoff and jitter
                delay = base_delay * (2 ** retry) + (random.random() * 0.1 * base_delay)
                
                if logger:
                    logger.warning(f"Attempt {retry + 1} failed: {e}. Retrying in {delay:.2f}s...")
                
                time.sleep(delay)
            except Exception as e:
                # For other exceptions, don't retry
                if logger:
                    logger.error(f"Error (not retrying): {format_error_for_logging(e)}")
                raise
        
        # This should not be reached
        if last_exception:
            raise last_exception
        raise RuntimeError("Retry logic failed unexpectedly")
