"""
Error handling and recovery strategies for Breaking Point MCP Agent.
"""

import logging
import time
import random
import functools
import traceback
from typing import Callable, Any, List, Dict, Optional, Type, TypeVar, cast

from .exceptions import (
    BPError, 
    APIError, 
    AuthenticationError, 
    NetworkError,
    TestError,
    RetryableError,
    format_error_for_logging
)

logger = logging.getLogger("BPAgent.ErrorHandler")

# Type variable for generic return type
T = TypeVar('T')

class RetryConfig:
    """Configuration for retry behavior"""
    
    def __init__(self, max_retries: int = 3, base_delay: float = 1.0,
                retry_exceptions: Optional[List[Type[Exception]]] = None,
                jitter: float = 0.1):
        """Initialize retry configuration
        
        Args:
            max_retries: Maximum number of retries
            base_delay: Base delay between retries in seconds
            retry_exceptions: List of exception types to retry on
            jitter: Jitter factor for randomizing delay
        """
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.retry_exceptions = retry_exceptions or [NetworkError, RetryableError]
        self.jitter = jitter
    
    def get_delay(self, retry: int) -> float:
        """Calculate delay for a specific retry attempt
        
        Args:
            retry: Current retry attempt (0-based)
            
        Returns:
            float: Delay in seconds
        """
        # Exponential backoff with jitter
        delay = self.base_delay * (2 ** retry)
        jitter_amount = delay * self.jitter * random.random()
        return delay + jitter_amount

def retry_with_backoff(retry_config: Optional[RetryConfig] = None) -> Callable:
    """Decorator for retrying a function with exponential backoff
    
    Args:
        retry_config: Retry configuration
        
    Returns:
        Callable: Decorated function
    """
    config = retry_config or RetryConfig()
    
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            last_exception = None
            
            for retry in range(config.max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except tuple(config.retry_exceptions) as e:
                    last_exception = e
                    
                    # Check if the error is retryable
                    if hasattr(e, 'retry_possible') and not e.retry_possible:
                        # Not retryable, re-raise immediately
                        raise
                    
                    # If this was the last retry, re-raise the exception
                    if retry >= config.max_retries:
                        if hasattr(e, 'retry_count'):
                            # Update retry count if it's a RetryableError
                            e.retry_count = retry
                            
                        logger.error(f"Failed after {retry + 1} attempts: {format_error_for_logging(e)}")
                        raise
                    
                    # Calculate delay
                    delay = config.get_delay(retry)
                    
                    logger.warning(f"Attempt {retry + 1} failed: {e}. Retrying in {delay:.2f}s...")
                    time.sleep(delay)
                except Exception as e:
                    # For other exceptions, don't retry
                    logger.error(f"Error (not retrying): {format_error_for_logging(e)}")
                    raise
            
            # This should not be reached
            if last_exception:
                raise last_exception
            raise RuntimeError("Retry logic failed unexpectedly")
            
        return wrapper
    
    return decorator

class ErrorContext:
    """Context manager for handling errors with context information"""
    
    def __init__(self, context_info: Dict[str, Any], 
                error_type: Type[BPError] = BPError,
                error_code: Optional[str] = None,
                recovery_func: Optional[Callable] = None):
        """Initialize error context
        
        Args:
            context_info: Context information to include in error
            error_type: Error type to raise if an exception occurs
            error_code: Error code to use in the raised error
            recovery_func: Function to call for recovery attempts
        """
        self.context_info = context_info
        self.error_type = error_type
        self.error_code = error_code
        self.recovery_func = recovery_func
    
    def __enter__(self):
        """Enter the context manager"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit the context manager
        
        Args:
            exc_type: Exception type
            exc_val: Exception value
            exc_tb: Exception traceback
            
        Returns:
            bool: True if the exception was handled, False otherwise
        """
        if exc_type is None:
            # No exception occurred
            return False
        
        # Attempt recovery if a recovery function is provided
        if self.recovery_func is not None and issubclass(exc_type, (APIError, TestError)):
            try:
                logger.info(f"Attempting recovery for {exc_type.__name__}: {exc_val}")
                self.recovery_func(exc_val)
                return True  # Exception handled
            except Exception as recovery_e:
                logger.error(f"Recovery failed: {recovery_e}")
                # Continue with normal error handling
        
        # Handle the exception
        if issubclass(exc_type, BPError):
            # Add context to existing BPError
            if hasattr(exc_val, 'details'):
                for key, value in self.context_info.items():
                    if key not in exc_val.details:
                        exc_val.details[key] = value
            
            logger.error(f"Error in context ({', '.join(f'{k}={v}' for k, v in self.context_info.items())}): {exc_val}")
            return False  # Re-raise the modified exception
        else:
            # Convert to BPError with context
            error_message = str(exc_val)
            error = self.error_type(
                error_message, 
                error_code=self.error_code,
                details=self.context_info
            )
            
            logger.error(f"Converted error in context: {format_error_for_logging(error)}")
            logger.debug(f"Original traceback: {''.join(traceback.format_exception(exc_type, exc_val, exc_tb))}")
            
            # Replace the exception
            raise error from exc_val
            
        return False

def safe_execute(func: Callable[..., T], 
                context_info: Dict[str, Any],
                error_type: Type[BPError] = BPError,
                error_code: Optional[str] = None,
                recovery_func: Optional[Callable] = None,
                *args: Any, **kwargs: Any) -> T:
    """Safely execute a function with error context
    
    Args:
        func: Function to execute
        context_info: Context information to include in error
        error_type: Error type to raise if an exception occurs
        error_code: Error code to use in the raised error
        recovery_func: Function to call for recovery attempts
        *args: Positional arguments for the function
        **kwargs: Keyword arguments for the function
        
    Returns:
        T: Result of the function
    """
    with ErrorContext(context_info, error_type, error_code, recovery_func):
        return func(*args, **kwargs)

def api_error_handler(error: APIError) -> None:
    """Handle API errors with appropriate responses
    
    Args:
        error: The API error to handle
    """
    # Log detailed information
    logger.error(f"API Error: {format_error_for_logging(error)}")
    
    # Check for specific error conditions
    if isinstance(error, AuthenticationError):
        logger.warning("Authentication failed. Please check your credentials.")
        # Could attempt to refresh credentials or token here
    
    elif isinstance(error, NetworkError):
        if error.is_timeout:
            logger.warning("Connection timed out. Check network and server status.")
        else:
            logger.warning("Network error. Check connectivity to the Breaking Point system.")
    
    elif error.status_code == 429:
        logger.warning("Rate limit exceeded. Waiting before retrying...")
        # Implement rate limiting handling
        time.sleep(10)
    
    elif 500 <= error.status_code < 600:
        logger.warning("Server error. The Breaking Point system may be experiencing issues.")
        
    else:
        logger.warning(f"Unexpected API error: {error.message}")

def test_error_handler(error: TestError) -> None:
    """Handle test errors with appropriate responses
    
    Args:
        error: The test error to handle
    """
    # Log detailed information
    logger.error(f"Test Error: {format_error_for_logging(error)}")
    
    # Check for specific error conditions
    if hasattr(error, 'test_id') and error.test_id:
        logger.info(f"Error occurred with test ID: {error.test_id}")
        if hasattr(error, 'run_id') and error.run_id:
            logger.info(f"Run ID: {error.run_id}")
            
            # Potential recovery actions based on error type
            if hasattr(error, 'details') and error.details.get('status') == 'error':
                logger.warning("Test run is in error state. Consider restarting the test.")

def handle_global_exception(exc_type, exc_val, exc_tb):
    """Global exception handler for uncaught exceptions
    
    Args:
        exc_type: Exception type
        exc_val: Exception value
        exc_tb: Exception traceback
        
    Returns:
        bool: True if the exception was handled, False otherwise
    """
    if issubclass(exc_type, BPError):
        logger.error(f"Uncaught BP error: {format_error_for_logging(exc_val)}")
    else:
        logger.error(f"Uncaught exception: {exc_val}")
        logger.debug(f"Traceback: {''.join(traceback.format_exception(exc_type, exc_val, exc_tb))}")
    
    # Return False to allow normal exception handling
    return False

# Set the global exception handler
sys.excepthook = handle_global_exception
