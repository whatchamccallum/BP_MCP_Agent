"""
Breaking Point API Interface
This module provides the interface to interact with the Breaking Point API.
"""

import logging
import requests
import time
from typing import Dict, List, Optional, Union, Any
from urllib3.exceptions import InsecureRequestWarning

from .exceptions import (
    APIError,
    AuthenticationError,
    NetworkError,
    ResourceNotFoundError,
    RetryableError
)
from .config import get_config
from .error_handler import retry_with_backoff, ErrorContext, api_error_handler

# Suppress insecure request warnings when using verify=False
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

logger = logging.getLogger("BPAgent.API")

class BreakingPointAPI:
    """Interface to the Breaking Point API"""
    
    def __init__(self, host: Optional[str] = None, username: Optional[str] = None, password: Optional[str] = None, 
                verify_ssl: Optional[bool] = None, timeout: Optional[int] = None):
        """Initialize the Breaking Point API interface
        
        Args:
            host: Breaking Point host address (default: from config)
            username: Breaking Point username (default: from config)
            password: Breaking Point password (default: from config)
            verify_ssl: Whether to verify SSL certificates (default: from config)
            timeout: Request timeout in seconds (default: from config)
        """
        # Get configuration
        config = get_config()
        api_config = config.get_api_config()
        credentials = config.get_credentials()
        
        # Set attributes from parameters or config
        self.host = host or api_config.get("host")
        self.username = username or credentials.get("username")
        self.password = password or credentials.get("password")
        self.verify_ssl = verify_ssl if verify_ssl is not None else api_config.get("verify_ssl", False)
        self.timeout = timeout or api_config.get("timeout", 60)
        self.retries = api_config.get("retries", 3)
        self.retry_delay = api_config.get("retry_delay", 5)
        
        if not self.host:
            raise ValueError("API host not specified and not found in configuration")
        if not self.username or not self.password:
            raise ValueError("API credentials not specified and not found in configuration")
            
        self.base_url = f"https://{self.host}/api/v1"
        self.session = requests.Session()
        self.auth_token = None
        
    @retry_with_backoff()
    def login(self) -> bool:
        """Log in to Breaking Point and get auth token
        
        Returns:
            bool: True if login successful, False otherwise
            
        Raises:
            AuthenticationError: If login fails due to invalid credentials
            NetworkError: If unable to connect to the Breaking Point system
        """
        context_info = {
            "host": self.host,
            "username": self.username[:3] + "***" if self.username else None  # Partial username for security
        }
        
        with ErrorContext(context_info, APIError, "LOGIN_ERROR"):
            try:
                login_url = f"{self.base_url}/auth/session"
                response = self.session.post(
                    login_url,
                    json={"username": self.username, "password": self.password},
                    verify=self.verify_ssl,
                    timeout=self.timeout
                )
                
                if response.status_code == 401:
                    logger.error(f"Failed to log in to Breaking Point: Invalid credentials")
                    raise AuthenticationError(
                        "Invalid username or password", 
                        status_code=401,
                        endpoint="auth/session"
                    )
                    
                response.raise_for_status()
                auth_data = response.json()
                self.auth_token = auth_data.get("token")
                
                if not self.auth_token:
                    logger.error("Authentication succeeded but no token received")
                    raise AuthenticationError(
                        "No authentication token received",
                        endpoint="auth/session"
                    )
                    
                self.session.headers.update({"X-API-KEY": self.auth_token})
                logger.info(f"Successfully logged in to Breaking Point at {self.host}")
                return True
                
            except requests.exceptions.ConnectionError as e:
                raise NetworkError(
                    f"Unable to connect to Breaking Point at {self.host}: {str(e)}",
                    endpoint="auth/session",
                    is_timeout=False
                )
                
            except requests.exceptions.Timeout as e:
                raise NetworkError(
                    f"Connection timeout to Breaking Point at {self.host}: {str(e)}",
                    endpoint="auth/session",
                    is_timeout=True
                )
                
            except requests.exceptions.HTTPError as e:
                status_code = e.response.status_code if hasattr(e, 'response') else None
                response_text = e.response.text if hasattr(e, 'response') else None
                
                raise APIError(
                    f"Login failed: {str(e)}",
                    status_code=status_code,
                    response=response_text,
                    endpoint="auth/session",
                    # Allow retry for server errors (5xx)
                    retry_possible=status_code is None or status_code >= 500
                )
                
            except requests.exceptions.RequestException as e:
                raise APIError(
                    f"Login failed: {str(e)}",
                    endpoint="auth/session"
                )
    
    def logout(self) -> bool:
        """Log out from Breaking Point
        
        Returns:
            bool: True if logout successful, False otherwise
        """
        try:
            if not self.auth_token:
                logger.debug("No active session to logout from")
                return True
                
            logout_url = f"{self.base_url}/auth/session"
            response = self.session.delete(
                logout_url, 
                verify=self.verify_ssl,
                timeout=self.timeout
            )
            
            response.raise_for_status()
            self.auth_token = None
            self.session.headers.pop("X-API-KEY", None)
            logger.info("Successfully logged out from Breaking Point")
            return True
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to log out from Breaking Point: {e}")
            # We don't raise exceptions here to avoid issues during cleanup
            return False
            
    @retry_with_backoff()
    def _api_call(self, method: str, endpoint: str, data: Optional[Dict] = None, params: Optional[Dict] = None) -> Any:
        """Make an API call to Breaking Point
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint
            data: Data to send, if any
            params: Query parameters, if any
            
        Returns:
            Any: Response from Breaking Point
            
        Raises:
            APIError: If the API call fails
            AuthenticationError: If not logged in
            ResourceNotFoundError: If the requested resource is not found
        """
        if not self.auth_token:
            raise AuthenticationError("Not logged in. Call login() first.")
            
        url = f"{self.base_url}/{endpoint}"
        context_info = {
            "method": method,
            "endpoint": endpoint,
            "host": self.host
        }
        
        with ErrorContext(context_info, APIError, "API_CALL_ERROR", api_error_handler):
            try:
                response = self.session.request(
                    method=method,
                    url=url,
                    json=data if data else None,
                    params=params,
                    verify=self.verify_ssl,
                    timeout=self.timeout
                )
                
                # Handle common status codes
                if response.status_code == 404:
                    raise ResourceNotFoundError(endpoint.split('/')[0], endpoint.split('/')[-1])
                    
                response.raise_for_status()
                
                # Parse and return response data
                if response.content:
                    try:
                        return response.json()
                    except ValueError:
                        # Not JSON, return text content
                        return {"raw_content": response.text}
                else:
                    return {}
                    
            except requests.exceptions.ConnectionError as e:
                raise NetworkError(
                    f"Connection error during API call to {endpoint}: {str(e)}",
                    endpoint=endpoint,
                    is_timeout=False
                )
                
            except requests.exceptions.Timeout as e:
                raise NetworkError(
                    f"Request timeout during API call to {endpoint}: {str(e)}",
                    endpoint=endpoint,
                    is_timeout=True
                )
                
            except requests.exceptions.HTTPError as e:
                status_code = e.response.status_code if hasattr(e, 'response') else None
                response_text = e.response.text if hasattr(e, 'response') else None
                
                # Determine if this error should be retried
                retry_possible = False
                if status_code:
                    # Retry server errors (5xx) and rate limit errors (429)
                    retry_possible = status_code >= 500 or status_code == 429
                    
                    # For rate limit errors, add some delay before retry
                    if status_code == 429:
                        time.sleep(2.0)
                
                raise APIError(
                    f"API call failed: {str(e)}",
                    status_code=status_code,
                    response=response_text,
                    endpoint=endpoint,
                    retry_possible=retry_possible
                )
                
            except requests.exceptions.RequestException as e:
                raise APIError(
                    f"API call to {endpoint} failed: {str(e)}",
                    endpoint=endpoint
                )
            
    # Test Management Methods
    def get_tests(self) -> List[Dict]:
        """Get all available tests
        
        Returns:
            List[Dict]: List of tests
            
        Raises:
            APIError: If the API call fails
        """
        return self._api_call("GET", "tests")
        
    def get_test(self, test_id: str) -> Dict:
        """Get test details
        
        Args:
            test_id: Test ID
            
        Returns:
            Dict: Test details
            
        Raises:
            APIError: If the API call fails
            ResourceNotFoundError: If the test is not found
        """
        return self._api_call("GET", f"tests/{test_id}")
        
    def create_test(self, test_config: Dict) -> Dict:
        """Create a new test
        
        Args:
            test_config: Test configuration
            
        Returns:
            Dict: Created test details
            
        Raises:
            APIError: If the API call fails
        """
        return self._api_call("POST", "tests", test_config)
        
    def update_test(self, test_id: str, test_config: Dict) -> Dict:
        """Update an existing test
        
        Args:
            test_id: Test ID
            test_config: Test configuration
            
        Returns:
            Dict: Updated test details
            
        Raises:
            APIError: If the API call fails
            ResourceNotFoundError: If the test is not found
        """
        return self._api_call("PUT", f"tests/{test_id}", test_config)
        
    def delete_test(self, test_id: str) -> Dict:
        """Delete a test
        
        Args:
            test_id: Test ID
            
        Returns:
            Dict: Response data
            
        Raises:
            APIError: If the API call fails
            ResourceNotFoundError: If the test is not found
        """
        return self._api_call("DELETE", f"tests/{test_id}")
        
    # Test Execution Methods
    def run_test(self, test_id: str) -> Dict:
        """Run a test
        
        Args:
            test_id: Test ID
            
        Returns:
            Dict: Response data including runId
            
        Raises:
            APIError: If the API call fails
            ResourceNotFoundError: If the test is not found
        """
        return self._api_call("POST", f"tests/{test_id}/operations/start")
        
    def stop_test(self, test_id: str) -> Dict:
        """Stop a running test
        
        Args:
            test_id: Test ID
            
        Returns:
            Dict: Response data
            
        Raises:
            APIError: If the API call fails
            ResourceNotFoundError: If the test is not found
        """
        return self._api_call("POST", f"tests/{test_id}/operations/stop")
        
    def get_test_results(self, test_id: str, run_id: str, use_cache: bool = True) -> Dict:
        """Get test results, optionally using cache
        
        Args:
            test_id: Test ID
            run_id: Run ID
            use_cache: Whether to use cached results if available
            
        Returns:
            Dict: Test results
            
        Raises:
            APIError: If the API call fails
            ResourceNotFoundError: If the test or run is not found
        """
        # Get cache config
        config = get_config()
        cache_config = config.get_cache_config()
        
        # Only use cache if enabled in config
        use_cache = use_cache and cache_config.get("enabled", True)
        
        # Check the cache first if enabled
        if use_cache:
            from .cache import get_cache
            cache = get_cache()
            cached_result = cache.get(test_id, run_id)
            if cached_result:
                logger.debug(f"Using cached result for test {test_id}, run {run_id}")
                return cached_result
            
        # Get results from API
        results = self._api_call("GET", f"tests/{test_id}/runs/{run_id}/results")
        
        # Cache the results if caching is enabled
        if use_cache:
            from .cache import get_cache
            cache = get_cache()
            cache.set(test_id, run_id, results)
            
        return results
        
    def get_test_status(self, test_id: str, run_id: str) -> str:
        """Get the current status of a test run
        
        Args:
            test_id: Test ID
            run_id: Run ID
            
        Returns:
            str: Test status (e.g., "running", "completed", "stopped")
            
        Raises:
            APIError: If the API call fails
            ResourceNotFoundError: If the test or run is not found
        """
        result = self._api_call("GET", f"tests/{test_id}/runs/{run_id}/status")
        return result.get("status", "unknown")
        
    # Network Elements Methods
    def get_network_elements(self) -> List[Dict]:
        """Get all network elements
        
        Returns:
            List[Dict]: List of network elements
            
        Raises:
            APIError: If the API call fails
        """
        return self._api_call("GET", "network/elements")
        
    def create_network_element(self, element_config: Dict) -> Dict:
        """Create a network element
        
        Args:
            element_config: Element configuration
            
        Returns:
            Dict: Created element details
            
        Raises:
            APIError: If the API call fails
        """
        return self._api_call("POST", "network/elements", element_config)
        
    # Super Flow Methods
    def get_superflows(self) -> List[Dict]:
        """Get all superflows
        
        Returns:
            List[Dict]: List of superflows
            
        Raises:
            APIError: If the API call fails
        """
        return self._api_call("GET", "superflows")
        
    def get_superflow(self, superflow_id: str) -> Dict:
        """Get superflow details
        
        Args:
            superflow_id: Superflow ID
            
        Returns:
            Dict: Superflow details
            
        Raises:
            APIError: If the API call fails
            ResourceNotFoundError: If the superflow is not found
        """
        return self._api_call("GET", f"superflows/{superflow_id}")
        
    def create_superflow(self, superflow_config: Dict) -> Dict:
        """Create a new superflow
        
        Args:
            superflow_config: Superflow configuration
            
        Returns:
            Dict: Created superflow details
            
        Raises:
            APIError: If the API call fails
        """
        return self._api_call("POST", "superflows", superflow_config)
        
    def update_superflow(self, superflow_id: str, superflow_config: Dict) -> Dict:
        """Update an existing superflow
        
        Args:
            superflow_id: Superflow ID
            superflow_config: Superflow configuration
            
        Returns:
            Dict: Updated superflow details
            
        Raises:
            APIError: If the API call fails
            ResourceNotFoundError: If the superflow is not found
        """
        return self._api_call("PUT", f"superflows/{superflow_id}", superflow_config)
        
    # Application Profiles Methods
    def get_app_profiles(self) -> List[Dict]:
        """Get all application profiles
        
        Returns:
            List[Dict]: List of application profiles
            
        Raises:
            APIError: If the API call fails
        """
        return self._api_call("GET", "appprofiles")
        
    def create_app_profile(self, profile_config: Dict) -> Dict:
        """Create a new application profile
        
        Args:
            profile_config: Profile configuration
            
        Returns:
            Dict: Created profile details
            
        Raises:
            APIError: If the API call fails
        """
        return self._api_call("POST", "appprofiles", profile_config)

    def get_bandwidth_components(self) -> List[Dict]:
        """Get all bandwidth test components
        
        Returns:
            List[Dict]: List of bandwidth components
            
        Raises:
            APIError: If the API call fails
        """
        return self._api_call("GET", "components/bandwidth")
        
    def create_bandwidth_component(self, component_config: Dict) -> Dict:
        """Create a new bandwidth test component
        
        Args:
            component_config: Component configuration
            
        Returns:
            Dict: Created component details
            
        Raises:
            APIError: If the API call fails
        """
        return self._api_call("POST", "components/bandwidth", component_config)
        
    # Strike Lists Methods
    def get_strike_lists(self) -> List[Dict]:
        """Get all strike lists
        
        Returns:
            List[Dict]: List of strike lists
            
        Raises:
            APIError: If the API call fails
        """
        return self._api_call("GET", "strikelists")
        
    def create_strike_list(self, strike_config: Dict) -> Dict:
        """Create a new strike list
        
        Args:
            strike_config: Strike list configuration
            
        Returns:
            Dict: Created strike list details
            
        Raises:
            APIError: If the API call fails
        """
        return self._api_call("POST", "strikelists", strike_config)
    
    def __enter__(self):
        """Context manager entry
        
        Returns:
            BreakingPointAPI: The API instance
            
        Raises:
            AuthenticationError: If login fails
        """
        self.login()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.logout()

# Factory function to create API instance from configuration
def create_api(host: Optional[str] = None, username: Optional[str] = None, 
              password: Optional[str] = None, verify_ssl: Optional[bool] = None) -> BreakingPointAPI:
    """Create a Breaking Point API instance from configuration
    
    Args:
        host: Breaking Point host address (default: from config)
        username: Breaking Point username (default: from config)
        password: Breaking Point password (default: from config)
        verify_ssl: Whether to verify SSL certificates (default: from config)
        
    Returns:
        BreakingPointAPI: API instance
    """
    return BreakingPointAPI(host, username, password, verify_ssl)
