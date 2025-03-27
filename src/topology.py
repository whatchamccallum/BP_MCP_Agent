"""
Network Topology Management
This module provides classes for managing network topologies in Breaking Point tests.
"""

import yaml
from typing import Dict, List

class NetworkTopology:
    """Manages network topology configurations"""
    
    def __init__(self):
        """Initialize the network topology"""
        self.client_networks = []
        self.server_networks = []
        self.dmz_networks = []
        self.external_networks = []
        
    def add_client_network(self, name: str, cidr: str, client_count: int):
        """Add a client network
        
        Args:
            name: Network name
            cidr: Network CIDR
            client_count: Number of clients
        """
        self.client_networks.append({
            "name": name,
            "cidr": cidr,
            "client_count": client_count,
            "type": "client"
        })
        
    def add_server_network(self, name: str, cidr: str, server_count: int):
        """Add a server network
        
        Args:
            name: Network name
            cidr: Network CIDR
            server_count: Number of servers
        """
        self.server_networks.append({
            "name": name,
            "cidr": cidr,
            "server_count": server_count,
            "type": "server"
        })
        
    def add_dmz_network(self, name: str, cidr: str):
        """Add a DMZ network
        
        Args:
            name: Network name
            cidr: Network CIDR
        """
        self.dmz_networks.append({
            "name": name,
            "cidr": cidr,
            "type": "dmz"
        })
        
    def add_external_network(self, name: str, cidr: str):
        """Add an external network
        
        Args:
            name: Network name
            cidr: Network CIDR
        """
        self.external_networks.append({
            "name": name,
            "cidr": cidr,
            "type": "external"
        })
        
    def to_dict(self) -> Dict:
        """Convert topology to dictionary
        
        Returns:
            Dict: Network topology configuration
        """
        return {
            "clientNetworks": self.client_networks,
            "serverNetworks": self.server_networks,
            "dmzNetworks": self.dmz_networks,
            "externalNetworks": self.external_networks
        }
        
    def from_dict(self, topology_dict: Dict):
        """Load topology from dictionary
        
        Args:
            topology_dict: Network topology configuration
        """
        self.client_networks = topology_dict.get("clientNetworks", [])
        self.server_networks = topology_dict.get("serverNetworks", [])
        self.dmz_networks = topology_dict.get("dmzNetworks", [])
        self.external_networks = topology_dict.get("externalNetworks", [])
        
    def to_file(self, filename: str):
        """Save topology to file
        
        Args:
            filename: Output filename
        """
        with open(filename, 'w') as f:
            yaml.dump(self.to_dict(), f)
            
    def from_file(self, filename: str):
        """Load topology from file
        
        Args:
            filename: Input filename
        """
        with open(filename, 'r') as f:
            topology_dict = yaml.safe_load(f)
            self.from_dict(topology_dict)

    def validate(self) -> bool:
        """Validate the network topology
        
        Returns:
            bool: True if the topology is valid, False otherwise
        """
        # Check for required networks
        if not self.client_networks:
            return False
            
        # Check CIDR formats
        for network in (self.client_networks + self.server_networks + 
                       self.dmz_networks + self.external_networks):
            cidr = network.get("cidr", "")
            if not self._is_valid_cidr(cidr):
                return False
                
        return True
        
    def _is_valid_cidr(self, cidr: str) -> bool:
        """Check if a CIDR is valid
        
        Args:
            cidr: CIDR to check
            
        Returns:
            bool: True if the CIDR is valid, False otherwise
        """
        if not cidr or "/" not in cidr:
            return False
            
        try:
            ip_part, mask_part = cidr.split("/")
            
            # Check IP part
            octets = ip_part.split(".")
            if len(octets) != 4:
                return False
                
            for octet in octets:
                value = int(octet)
                if value < 0 or value > 255:
                    return False
                    
            # Check mask part
            mask = int(mask_part)
            if mask < 0 or mask > 32:
                return False
                
            return True
        except ValueError:
            return False
