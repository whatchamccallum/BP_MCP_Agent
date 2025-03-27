"""
Asynchronous Breaking Point API Interface
This module provides asynchronous interaction with the Breaking Point API.
"""

import logging
import asyncio
import aiohttp
from typing import Dict, List, Optional, Union, Any
from urllib3.exceptions import InsecureRequestWarning

from .exceptions import (
    APIError,
    AuthenticationError,
    NetworkError,
    ResourceNotFoundError
)

# Configure module logger
logger = logging.getLogger("BPAgent.AsyncAPI")

class AsyncBreakingPointAPI:
    """Asynchronous interface to the Breaking Point API"""
    
    def __init__(self, host: str, username: str, password: str, verify_ssl: bool = False, timeout: int = 60):
        """Initialize the asynchronous Breaking Point API interface
        
        Args:
            host: Breaking Point host address
            username: Breaking Point username
            password: Breaking Point password
            verify_ssl: Whether to verify SSL certificates
            timeout: Request timeout in seconds
        """
        self.host = host
        self.username = username
        self.password = password
        self.base_url = f"https://{host}/api/v1"
        self.session = None
        self.auth_token = None
        self.verify_ssl = verify_ssl
        self.timeout = timeout
        
    async def __aenter__(self):
        """Async context manager entry
        
        Returns:
            AsyncBreakingPointAPI: The API instance
            
        Raises:
            AuthenticationError: If login fails
        """
        await self.login()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.logout()
        if self.session and not self.session.closed:
            await self.session.close()
            
    async def _create_session(self):
        """Create an aiohttp session if not already created"""
        if self.session is None or self.session.closed:
            ssl = None if not self.verify_ssl else True
            timeout = aiohttp.ClientTimeout(total=self.timeout)
            self.session = aiohttp.ClientSession(timeout=timeout)
        
    async def login(self) -> bool:
        """Asynchronously log in to Breaking Point and get auth token
        
        Returns:
            bool: True if login successful
            
        Raises:
            AuthenticationError: If login fails due to invalid credentials
            NetworkError: If unable to connect to the Breaking Point system
        """
        await self._create_session()
        
        try:
            login_url = f"{self.base_url}/auth/session"
            async with self.session.post(
                login_url,
                json={"username": self.username, "password": self.password},
                ssl=None if not self.verify_ssl else True,
            ) as response:
                if response.status == 401:
                    logger.error("Failed to log in to Breaking Point: Invalid credentials")
                    raise AuthenticationError("Invalid username or password", status_code=401)
                    
                response.raise_for_status()
                auth_data = await response.json()
                self.auth_token = auth_data.get("token")
                
                if not self.auth_token:
                    logger.error("Authentication succeeded but no token received")
                    raise AuthenticationError("No authentication token received")
                    
                logger.info(f"Successfully logged in to Breaking Point at {self.host}")
                return True
                
        except aiohttp.ClientConnectorError as e:
            logger.error(f"Network error connecting to Breaking Point: {e}")
            raise NetworkError(f"Unable to connect to Breaking Point at {self.host}: {str(e)}")
            
        except aiohttp.ClientTimeout as e:
            logger.error(f"Connection timeout to Breaking Point: {e}")
            raise NetworkError(f"Connection timeout to Breaking Point at {self.host}: {str(e)}")
            
        except aiohttp.ClientResponseError as e:
            logger.error(f"Failed to log in to Breaking Point: {e}")
            raise APIError(
                f"Login failed: {str(e)}", 
                status_code=e.status,
                response=str(e),
                endpoint="auth/session"
            )
            
        except Exception as e:
            logger.error(f"Failed to log in to Breaking Point: {e}")
            raise APIError(f"Login failed: {str(e)}")
    
    async def logout(self) -> bool:
        """Asynchronously log out from Breaking Point
        
        Returns:
            bool: True if logout successful, False otherwise
        """
        if not self.session or not self.auth_token:
            logger.debug("No active session to logout from")
            return True
            
        try:
            logout_url = f"{self.base_url}/auth/session"
            headers = {"X-API-KEY": self.auth_token}
            
            async with self.session.delete(
                logout_url,
                headers=headers,
                ssl=None if not self.verify_ssl else True,
            ) as response:
                response.raise_for_status()
                self.auth_token = None
                logger.info("Successfully logged out from Breaking Point")
                return True
                
        except Exception as e:
            logger.error(f"Failed to log out from Breaking Point: {e}")
            # We don't raise exceptions here to avoid issues during cleanup
            return False
            
    async def _api_call(self, method: str, endpoint: str, data: Optional[Dict] = None, params: Optional[Dict] = None) -> Any:
        """Make an asynchronous API call to Breaking Point
        
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
            
        await self._create_session()
        url = f"{self.base_url}/{endpoint}"
        headers = {"X-API-KEY": self.auth_token}
        
        try:
            async with self.session.request(
                method=method,
                url=url,
                headers=headers,
                json=data if data else None,
                params=params,
                ssl=None if not self.verify_ssl else True,
            ) as response:
                # Handle common status codes
                if response.status == 404:
                    raise ResourceNotFoundError(endpoint.split('/')[0], endpoint.split('/')[-1])
                    
                response.raise_for_status()
                if response.content_type == 'application/json':
                    return await response.json()
                else:
                    return await response.text()
                
        except aiohttp.ClientConnectorError as e:
            logger.error(f"Network error during API call to {endpoint}: {e}")
            raise NetworkError(f"Connection error during API call to {endpoint}: {str(e)}")
            
        except aiohttp.ClientTimeout as e:
            logger.error(f"Timeout during API call to {endpoint}: {e}")
            raise NetworkError(f"Request timeout during API call to {endpoint}: {str(e)}")
            
        except aiohttp.ClientResponseError as e:
            logger.error(f"HTTP error during API call to {endpoint}: {e.status} - {e}")
            raise APIError(
                f"API call failed: {str(e)}",
                status_code=e.status,
                response=str(e),
                endpoint=endpoint
            )
            
        except Exception as e:
            logger.error(f"API call to {endpoint} failed: {e}")
            raise APIError(f"API call to {endpoint} failed: {str(e)}")
            
    # Test Management Methods
    async def get_tests(self) -> List[Dict]:
        """Asynchronously get all available tests
        
        Returns:
            List[Dict]: List of tests
            
        Raises:
            APIError: If the API call fails
        """
        return await self._api_call("GET", "tests")
        
    async def get_test(self, test_id: str) -> Dict:
        """Asynchronously get test details
        
        Args:
            test_id: Test ID
            
        Returns:
            Dict: Test details
            
        Raises:
            APIError: If the API call fails
            ResourceNotFoundError: If the test is not found
        """
        return await self._api_call("GET", f"tests/{test_id}")
        
    async def create_test(self, test_config: Dict) -> Dict:
        """Asynchronously create a new test
        
        Args:
            test_config: Test configuration
            
        Returns:
            Dict: Created test details
            
        Raises:
            APIError: If the API call fails
        """
        return await self._api_call("POST", "tests", test_config)
        
    async def update_test(self, test_id: str, test_config: Dict) -> Dict:
        """Asynchronously update an existing test
        
        Args:
            test_id: Test ID
            test_config: Test configuration
            
        Returns:
            Dict: Updated test details
            
        Raises:
            APIError: If the API call fails
            ResourceNotFoundError: If the test is not found
        """
        return await self._api_call("PUT", f"tests/{test_id}", test_config)
        
    async def delete_test(self, test_id: str) -> Dict:
        """Asynchronously delete a test
        
        Args:
            test_id: Test ID
            
        Returns:
            Dict: Response data
            
        Raises:
            APIError: If the API call fails
            ResourceNotFoundError: If the test is not found
        """
        return await self._api_call("DELETE", f"tests/{test_id}")
        
    # Test Execution Methods
    async def run_test(self, test_id: str) -> Dict:
        """Asynchronously run a test
        
        Args:
            test_id: Test ID
            
        Returns:
            Dict: Response data including runId
            
        Raises:
            APIError: If the API call fails
            ResourceNotFoundError: If the test is not found
        """
        return await self._api_call("POST", f"tests/{test_id}/operations/start")
        
    async def stop_test(self, test_id: str) -> Dict:
        """Asynchronously stop a running test
        
        Args:
            test_id: Test ID
            
        Returns:
            Dict: Response data
            
        Raises:
            APIError: If the API call fails
            ResourceNotFoundError: If the test is not found
        """
        return await self._api_call("POST", f"tests/{test_id}/operations/stop")
        
    async def get_test_results(self, test_id: str, run_id: str, use_cache: bool = True) -> Dict:
        """Asynchronously get test results, optionally using cache
        
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
        # Check the cache first if enabled
        if use_cache:
            from .cache import get_cache
            cache = get_cache()
            cached_result = cache.get(test_id, run_id)
            if cached_result:
                logger.debug(f"Using cached result for test {test_id}, run {run_id}")
                return cached_result
            
        # Get results from API
        results = await self._api_call("GET", f"tests/{test_id}/runs/{run_id}/results")
        
        # Cache the results if caching is enabled
        if use_cache:
            from .cache import get_cache
            cache = get_cache()
            cache.set(test_id, run_id, results)
            
        return results
        
    async def get_test_status(self, test_id: str, run_id: str) -> str:
        """Asynchronously get the current status of a test run
        
        Args:
            test_id: Test ID
            run_id: Run ID
            
        Returns:
            str: Test status (e.g., "running", "completed", "stopped")
            
        Raises:
            APIError: If the API call fails
            ResourceNotFoundError: If the test or run is not found
        """
        result = await self._api_call("GET", f"tests/{test_id}/runs/{run_id}/status")
        return result.get("status", "unknown")
        
    # Network Elements Methods
    async def get_network_elements(self) -> List[Dict]:
        """Asynchronously get all network elements
        
        Returns:
            List[Dict]: List of network elements
            
        Raises:
            APIError: If the API call fails
        """
        return await self._api_call("GET", "network/elements")
        
    async def create_network_element(self, element_config: Dict) -> Dict:
        """Asynchronously create a network element
        
        Args:
            element_config: Element configuration
            
        Returns:
            Dict: Created element details
            
        Raises:
            APIError: If the API call fails
        """
        return await self._api_call("POST", "network/elements", element_config)
        
    # Super Flow Methods
    async def get_superflows(self) -> List[Dict]:
        """Asynchronously get all superflows
        
        Returns:
            List[Dict]: List of superflows
            
        Raises:
            APIError: If the API call fails
        """
        return await self._api_call("GET", "superflows")
        
    async def get_superflow(self, superflow_id: str) -> Dict:
        """Asynchronously get superflow details
        
        Args:
            superflow_id: Superflow ID
            
        Returns:
            Dict: Superflow details
            
        Raises:
            APIError: If the API call fails
            ResourceNotFoundError: If the superflow is not found
        """
        return await self._api_call("GET", f"superflows/{superflow_id}")
        
    async def create_superflow(self, superflow_config: Dict) -> Dict:
        """Asynchronously create a new superflow
        
        Args:
            superflow_config: Superflow configuration
            
        Returns:
            Dict: Created superflow details
            
        Raises:
            APIError: If the API call fails
        """
        return await self._api_call("POST", "superflows", superflow_config)
        
    async def update_superflow(self, superflow_id: str, superflow_config: Dict) -> Dict:
        """Asynchronously update an existing superflow
        
        Args:
            superflow_id: Superflow ID
            superflow_config: Superflow configuration
            
        Returns:
            Dict: Updated superflow details
            
        Raises:
            APIError: If the API call fails
            ResourceNotFoundError: If the superflow is not found
        """
        return await self._api_call("PUT", f"superflows/{superflow_id}", superflow_config)
        
    # Application Profiles Methods
    async def get_app_profiles(self) -> List[Dict]:
        """Asynchronously get all application profiles
        
        Returns:
            List[Dict]: List of application profiles
            
        Raises:
            APIError: If the API call fails
        """
        return await self._api_call("GET", "appprofiles")
        
    async def create_app_profile(self, profile_config: Dict) -> Dict:
        """Asynchronously create a new application profile
        
        Args:
            profile_config: Profile configuration
            
        Returns:
            Dict: Created profile details
            
        Raises:
            APIError: If the API call fails
        """
        return await self._api_call("POST", "appprofiles", profile_config)

    async def get_bandwidth_components(self) -> List[Dict]:
        """Asynchronously get all bandwidth test components
        
        Returns:
            List[Dict]: List of bandwidth components
            
        Raises:
            APIError: If the API call fails
        """
        return await self._api_call("GET", "components/bandwidth")
        
    async def create_bandwidth_component(self, component_config: Dict) -> Dict:
        """Asynchronously create a new bandwidth test component
        
        Args:
            component_config: Component configuration
            
        Returns:
            Dict: Created component details
            
        Raises:
            APIError: If the API call fails
        """
        return await self._api_call("POST", "components/bandwidth", component_config)
        
    # Strike Lists Methods
    async def get_strike_lists(self) -> List[Dict]:
        """Asynchronously get all strike lists
        
        Returns:
            List[Dict]: List of strike lists
            
        Raises:
            APIError: If the API call fails
        """
        return await self._api_call("GET", "strikelists")
        
    async def create_strike_list(self, strike_config: Dict) -> Dict:
        """Asynchronously create a new strike list
        
        Args:
            strike_config: Strike list configuration
            
        Returns:
            Dict: Created strike list details
            
        Raises:
            APIError: If the API call fails
        """
        return await self._api_call("POST", "strikelists", strike_config)

    # Helper methods
    async def run_multiple_tests(self, test_ids: List[str]) -> Dict[str, str]:
        """Run multiple tests concurrently
        
        Args:
            test_ids: List of test IDs to run
            
        Returns:
            Dict[str, str]: Mapping of test_id to run_id
        """
        tasks = [self.run_test(test_id) for test_id in test_ids]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        run_ids = {}
        for i, result in enumerate(results):
            test_id = test_ids[i]
            if isinstance(result, Exception):
                logger.error(f"Failed to run test {test_id}: {result}")
                run_ids[test_id] = None
            else:
                run_ids[test_id] = result.get("runId")
                
        return run_ids
        
    async def wait_for_tests_completion(self, test_runs: Dict[str, str], poll_interval: int = 10) -> Dict[str, str]:
        """Wait for multiple tests to complete
        
        Args:
            test_runs: Mapping of test_id to run_id
            poll_interval: Polling interval in seconds
            
        Returns:
            Dict[str, str]: Mapping of test_id to final status
        """
        pending_tests = {test_id: run_id for test_id, run_id in test_runs.items() if run_id is not None}
        final_status = {}
        
        while pending_tests:
            # Create tasks to check status for all pending tests
            status_tasks = [
                self.get_test_status(test_id, run_id) 
                for test_id, run_id in pending_tests.items()
            ]
            
            # Wait for all status checks to complete
            statuses = await asyncio.gather(*status_tasks, return_exceptions=True)
            
            # Process results
            tests_to_remove = []
            for i, (test_id, run_id) in enumerate(pending_tests.items()):
                status = statuses[i]
                
                if isinstance(status, Exception):
                    logger.error(f"Failed to get status for test {test_id}, run {run_id}: {status}")
                    final_status[test_id] = "error"
                    tests_to_remove.append(test_id)
                    continue
                    
                if status in ["completed", "stopped", "error", "failed"]:
                    final_status[test_id] = status
                    tests_to_remove.append(test_id)
                    logger.info(f"Test {test_id}, run {run_id} completed with status: {status}")
            
            # Remove completed tests from pending list
            for test_id in tests_to_remove:
                del pending_tests[test_id]
                
            # If there are still pending tests, wait before polling again
            if pending_tests:
                logger.debug(f"Waiting for {len(pending_tests)} tests to complete")
                await asyncio.sleep(poll_interval)
                
        return final_status
        
    async def get_multiple_test_results(self, test_runs: Dict[str, str], use_cache: bool = True) -> Dict[str, Dict]:
        """Get results for multiple tests concurrently
        
        Args:
            test_runs: Mapping of test_id to run_id
            use_cache: Whether to use cached results if available
            
        Returns:
            Dict[str, Dict]: Mapping of test_id to test results
        """
        result_tasks = [
            self.get_test_results(test_id, run_id, use_cache=use_cache)
            for test_id, run_id in test_runs.items()
            if run_id is not None
        ]
        
        results = await asyncio.gather(*result_tasks, return_exceptions=True)
        
        # Map results back to test IDs
        test_results = {}
        i = 0
        for test_id, run_id in test_runs.items():
            if run_id is not None:
                result = results[i]
                if isinstance(result, Exception):
                    logger.error(f"Failed to get results for test {test_id}, run {run_id}: {result}")
                    test_results[test_id] = {"error": str(result)}
                else:
                    test_results[test_id] = result
                i += 1
            else:
                test_results[test_id] = {"error": "Test did not start successfully"}
                
        return test_results
