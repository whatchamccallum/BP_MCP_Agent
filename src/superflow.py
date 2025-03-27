"""
SuperFlow Management
This module provides classes for managing SuperFlows and flows in Breaking Point.
"""

import logging
from typing import Dict, List

from .api import BreakingPointAPI

logger = logging.getLogger("BPAgent.SuperFlow")

class SuperFlowManager:
    """Manages SuperFlows and flows for application simulations"""
    
    def __init__(self, bp_api: BreakingPointAPI):
        """Initialize the SuperFlow manager
        
        Args:
            bp_api: Breaking Point API instance
        """
        self.bp_api = bp_api
        
    def create_basic_superflow(self, name: str, protocol: str) -> Dict:
        """Create a basic SuperFlow with a single flow
        
        Args:
            name: SuperFlow name
            protocol: Protocol to use (HTTP, FTP, etc.)
            
        Returns:
            Dict: Created SuperFlow details
        """
        # Basic structure of a SuperFlow with a single flow
        superflow_config = {
            "name": name,
            "weight": 1,
            "flows": [
                {
                    "name": f"{protocol} Flow",
                    "protocol": protocol,
                    "type": "STANDARD",
                    "actions": []
                }
            ]
        }
        
        # Add default actions based on protocol
        if protocol == "HTTP":
            superflow_config["flows"][0]["actions"] = [
                {
                    "actionType": "GET",
                    "source": "client",
                    "destination": "server",
                    "path": "/index.html"
                },
                {
                    "actionType": "RESPONSE",
                    "source": "server",
                    "destination": "client",
                    "statusCode": 200,
                    "contentType": "text/html"
                }
            ]
        elif protocol == "FTP":
            superflow_config["flows"][0]["actions"] = [
                {
                    "actionType": "CONNECT",
                    "source": "client",
                    "destination": "server"
                },
                {
                    "actionType": "LOGIN",
                    "source": "client",
                    "destination": "server",
                    "username": "anonymous",
                    "password": "anonymous@"
                },
                {
                    "actionType": "GETFILE",
                    "source": "client",
                    "destination": "server",
                    "filename": "test.txt"
                }
            ]
            
        return self.bp_api.create_superflow(superflow_config)
    
    def add_action_to_flow(self, superflow_id: str, flow_index: int, action: Dict) -> Dict:
        """Add an action to a flow in a SuperFlow
        
        Args:
            superflow_id: SuperFlow ID
            flow_index: Index of the flow to modify
            action: Action to add
            
        Returns:
            Dict: Updated SuperFlow details
        """
        # Get current SuperFlow
        superflow = self.bp_api.get_superflow(superflow_id)
        
        # Add action to the specified flow
        if flow_index < len(superflow.get("flows", [])):
            superflow["flows"][flow_index]["actions"].append(action)
            return self.bp_api.update_superflow(superflow_id, superflow)
        else:
            raise ValueError(f"Flow index {flow_index} out of range")
    
    def create_http_superflow(self, name: str, transactions: List[Dict]) -> Dict:
        """Create an HTTP SuperFlow with multiple transactions
        
        Args:
            name: SuperFlow name
            transactions: List of transactions (request/response pairs)
            
        Returns:
            Dict: Created SuperFlow details
        """
        # Initialize SuperFlow
        superflow_config = {
            "name": name,
            "weight": 1,
            "flows": [
                {
                    "name": "HTTP Flow",
                    "protocol": "HTTP",
                    "type": "STANDARD",
                    "actions": []
                }
            ]
        }
        
        # Add all transactions
        actions = []
        for transaction in transactions:
            # Add request
            actions.append({
                "actionType": transaction.get("method", "GET"),
                "source": "client",
                "destination": "server",
                "path": transaction.get("path", "/"),
                "headers": transaction.get("request_headers", {}),
                "body": transaction.get("request_body", "")
            })
            
            # Add response
            actions.append({
                "actionType": "RESPONSE",
                "source": "server",
                "destination": "client",
                "statusCode": transaction.get("status_code", 200),
                "contentType": transaction.get("content_type", "text/html"),
                "headers": transaction.get("response_headers", {}),
                "body": transaction.get("response_body", "")
            })
            
        superflow_config["flows"][0]["actions"] = actions
        return self.bp_api.create_superflow(superflow_config)
