"""
Test Builder Module
This module provides classes for building different types of Breaking Point tests.
"""

import logging
from typing import Dict, List

from .api import BreakingPointAPI
from .topology import NetworkTopology

logger = logging.getLogger("BPAgent.TestBuilder")

class TestBuilder:
    """Builds different types of Breaking Point tests"""
    
    def __init__(self, bp_api: BreakingPointAPI):
        """Initialize the test builder
        
        Args:
            bp_api: Breaking Point API instance
        """
        self.bp_api = bp_api
        
    def create_strike_test(self, 
                          name: str, 
                          strike_list_id: str, 
                          topology: NetworkTopology,
                          duration: int = 60) -> Dict:
        """Create a strike test
        
        Args:
            name: Test name
            strike_list_id: Strike list ID
            topology: Network topology
            duration: Test duration in seconds
            
        Returns:
            Dict: Test configuration
        """
        # Basic structure of a Strike test
        test_config = {
            "name": name,
            "type": "strike",
            "duration": duration,
            "networkConfig": topology.to_dict(),
            "strikeConfig": {
                "strikeListId": strike_list_id,
                "evasionProfile": "Default",
            }
        }
        
        return self.bp_api.create_test(test_config)
        
    def create_app_sim_test(self,
                           name: str,
                           app_profile_id: str,
                           topology: NetworkTopology,
                           duration: int = 60) -> Dict:
        """Create an application simulation test
        
        Args:
            name: Test name
            app_profile_id: Application profile ID
            topology: Network topology
            duration: Test duration in seconds
            
        Returns:
            Dict: Test configuration
        """
        # Basic structure of an Application Simulation test
        test_config = {
            "name": name,
            "type": "appsim",
            "duration": duration,
            "networkConfig": topology.to_dict(),
            "appConfig": {
                "appProfileId": app_profile_id,
                "rateModeEnabled": True,
                "rateMode": "mbps",
                "rate": 100  # Default 100 Mbps
            }
        }
        
        return self.bp_api.create_test(test_config)
        
    def create_client_sim_test(self,
                              name: str,
                              client_profile_id: str,
                              topology: NetworkTopology,
                              duration: int = 60) -> Dict:
        """Create a client simulation test
        
        Args:
            name: Test name
            client_profile_id: Client profile ID
            topology: Network topology
            duration: Test duration in seconds
            
        Returns:
            Dict: Test configuration
        """
        # Basic structure of a Client Simulation test
        test_config = {
            "name": name,
            "type": "clientsim",
            "duration": duration,
            "networkConfig": topology.to_dict(),
            "clientConfig": {
                "clientProfileId": client_profile_id,
                "concurrent": 1000,  # Default concurrent connections
                "open": 50000,  # Default total connections
                "close": 50000,  # Default close connections
                "tps": 1000  # Default transactions per second
            }
        }
        
        return self.bp_api.create_test(test_config)
        
    def create_bandwidth_test(self,
                             name: str,
                             bandwidth_component_id: str,
                             topology: NetworkTopology,
                             duration: int = 60,
                             rate: int = 1000,  # 1Gbps default
                             frame_size: int = 1024,
                             buffer_size: int = 65536) -> Dict:
        """Create a bandwidth test
        
        Args:
            name: Test name
            bandwidth_component_id: Bandwidth component ID
            topology: Network topology
            duration: Test duration in seconds
            rate: Bandwidth rate in Mbps
            frame_size: Frame size in bytes
            buffer_size: Buffer size in bytes
            
        Returns:
            Dict: Test configuration
        """
        # Basic structure of a Bandwidth test
        test_config = {
            "name": name,
            "type": "bandwidth",
            "duration": duration,
            "networkConfig": topology.to_dict(),
            "bandwidthConfig": {
                "componentId": bandwidth_component_id,
                "rate": rate,
                "rateUnit": "mbps",
                "frameSize": frame_size,
                "bufferSize": buffer_size,
                "direction": "bidirectional",  # Can be: unidirectional, bidirectional
                "loadType": "constant"  # Can be: constant, step, ramp
            }
        }
        
        return self.bp_api.create_test(test_config)
        
    def create_advanced_security_test(self,
                                     name: str,
                                     strike_list_ids: List[str],
                                     evasion_profile: str = "Default",
                                     topology: NetworkTopology = None,
                                     duration: int = 60,
                                     concurrent_strikes: int = 1,
                                     random_seed: int = 1,
                                     targets: List[Dict] = None) -> Dict:
        """Create an advanced security test with multiple strike lists and targeted hosts
        
        Args:
            name: Test name
            strike_list_ids: List of strike list IDs to include
            evasion_profile: Evasion profile name
            topology: Network topology (optional, will use default if not provided)
            duration: Test duration in seconds
            concurrent_strikes: Number of concurrent strikes to run
            random_seed: Random seed for reproducibility
            targets: List of specific target host configurations
            
        Returns:
            Dict: Test configuration
        """
        # Use default topology if none provided
        if topology is None:
            topology = NetworkTopology()
            # Add basic networks
            topology.add_client_network("Client-Net-1", "10.10.1.0/24", 100)
            topology.add_server_network("Server-Net-1", "10.20.1.0/24", 10)
            
        # Default target if none specified
        if not targets:
            targets = [{
                "targetType": "allHosts",  # Can be allHosts, networkRange, hostList
                "direction": "both",  # Can be source, destination, both
            }]
        
        # Configure the strike components
        strike_components = []
        for strike_list_id in strike_list_ids:
            strike_components.append({
                "strikeListId": strike_list_id,
                "evasionProfile": evasion_profile,
                "weight": 1
            })
            
        # Basic structure of an Advanced Security test
        test_config = {
            "name": name,
            "type": "security",
            "duration": duration,
            "networkConfig": topology.to_dict(),
            "securityConfig": {
                "strikeComponents": strike_components,
                "concurrentStrikes": concurrent_strikes,
                "randomSeed": random_seed,
                "targets": targets,
                "options": {
                    "enableTcpRst": True,  # Send TCP RST packets to close connections
                    "enableUniqueMac": True,  # Use unique MAC addresses
                    "disableArpResolution": False  # Enable ARP resolution
                }
            }
        }
        
        return self.bp_api.create_test(test_config)
