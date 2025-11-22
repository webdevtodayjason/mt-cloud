"""
MikroTik RouterOS API Service
Handles connections to MikroTik devices and retrieves metrics
"""
import routeros_api
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class MikroTikConnectionError(Exception):
    """Raised when connection to MikroTik device fails"""
    pass


class MikroTikService:
    """Service for interacting with MikroTik devices via RouterOS API"""
    
    def __init__(self, host: str, username: str, password: str, port: int = 8728, use_ssl: bool = False):
        """
        Initialize MikroTik connection
        
        Args:
            host: IP address or hostname of MikroTik device
            username: RouterOS username (must have API access)
            password: RouterOS password
            port: API port (default 8728, or 8729 for SSL)
            use_ssl: Whether to use SSL connection
        """
        self.host = host
        self.username = username
        self.password = password
        self.port = port
        self.use_ssl = use_ssl
        self.connection = None
        
    def connect(self) -> bool:
        """
        Establish connection to MikroTik device
        
        Returns:
            bool: True if connection successful
            
        Raises:
            MikroTikConnectionError: If connection fails
        """
        try:
            self.connection = routeros_api.RouterOsApiPool(
                host=self.host,
                username=self.username,
                password=self.password,
                port=self.port,
                use_ssl=self.use_ssl,
                plaintext_login=True
            )
            # Test connection by getting API
            api = self.connection.get_api()
            logger.info(f"Successfully connected to MikroTik device at {self.host}")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to {self.host}: {str(e)}")
            raise MikroTikConnectionError(f"Connection failed: {str(e)}")
    
    def disconnect(self):
        """Close connection to MikroTik device"""
        if self.connection:
            self.connection.disconnect()
            self.connection = None
            logger.info(f"Disconnected from {self.host}")
    
    def get_system_identity(self) -> Dict[str, Any]:
        """Get system identity/hostname"""
        api = self.connection.get_api()
        resource = api.get_resource('/system/identity')
        result = resource.get()
        return result[0] if result else {}
    
    def get_system_resources(self) -> Dict[str, Any]:
        """
        Get system resource information (CPU, memory, uptime)
        
        Returns:
            Dict containing:
                - platform: Hardware platform
                - version: RouterOS version
                - cpu-load: CPU load percentage
                - free-memory: Free memory in bytes
                - total-memory: Total memory in bytes
                - uptime: System uptime
                - architecture-name: CPU architecture
        """
        api = self.connection.get_api()
        resource = api.get_resource('/system/resource')
        result = resource.get()
        return result[0] if result else {}
    
    def get_interfaces(self) -> list[Dict[str, Any]]:
        """
        Get list of all network interfaces
        
        Returns:
            List of interface dictionaries with name, type, mac-address, etc.
        """
        api = self.connection.get_api()
        resource = api.get_resource('/interface')
        return resource.get()
    
    def get_interface_stats(self, interface_name: str) -> Dict[str, Any]:
        """
        Get real-time statistics for a specific interface
        
        Args:
            interface_name: Name of interface (e.g., 'ether1', 'sfp-sfpplus1')
            
        Returns:
            Dict with rx-bits-per-second, tx-bits-per-second, etc.
        """
        api = self.connection.get_api()
        stats = api.get_resource('/interface').call(
            'monitor-traffic',
            {'interface': interface_name, 'once': ''}
        )
        return stats[0] if stats else {}
    
    def get_all_interface_stats(self) -> Dict[str, Any]:
        """Get statistics for all interfaces at once"""
        api = self.connection.get_api()
        resource = api.get_resource('/interface')
        return resource.get()
    
    def get_dhcp_leases(self) -> list[Dict[str, Any]]:
        """Get list of DHCP leases"""
        api = self.connection.get_api()
        resource = api.get_resource('/ip/dhcp-server/lease')
        return resource.get()
    
    def get_ip_addresses(self) -> list[Dict[str, Any]]:
        """Get configured IP addresses"""
        api = self.connection.get_api()
        resource = api.get_resource('/ip/address')
        return resource.get()
    
    def test_connection(self) -> Dict[str, Any]:
        """
        Test connection and return basic device info
        
        Returns:
            Dict with success status and device information
        """
        try:
            self.connect()
            
            identity = self.get_system_identity()
            resources = self.get_system_resources()
            
            result = {
                "success": True,
                "host": self.host,
                "identity": identity.get('name', 'Unknown'),
                "version": resources.get('version', 'Unknown'),
                "platform": resources.get('board-name', 'Unknown'),
                "uptime": resources.get('uptime', 'Unknown'),
                "cpu_load": resources.get('cpu-load', 0),
                "free_memory": resources.get('free-memory', 0),
                "total_memory": resources.get('total-memory', 0),
            }
            
            self.disconnect()
            return result
            
        except Exception as e:
            return {
                "success": False,
                "host": self.host,
                "error": str(e)
            }
    
    def __enter__(self):
        """Context manager support"""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager cleanup"""
        self.disconnect()
