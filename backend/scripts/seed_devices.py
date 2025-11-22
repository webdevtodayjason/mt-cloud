#!/usr/bin/env python3
"""
Seed database with MikroTik devices
"""
import sys
from pathlib import Path
import requests

backend_path = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_path))

API_BASE = "http://localhost:8001"

DEVICES = [
    {
        "name": "Main Router",
        "ip_address": "192.168.100.1",
        "port": 8728,
        "username": "admin",
        "password": "Dragon@123!@#",
        "device_type": "router",
        "model": "CRS310-8G+2S+",
        "site_id": 1,  # We'll need to create a site first
        "use_ssl": False
    },
    {
        "name": "10G Switch",
        "ip_address": "192.168.100.2",
        "port": 8728,
        "username": "admin",
        "password": "Dragon@123!@#",
        "device_type": "switch",
        "model": "CRS309-1G-8S+",
        "site_id": 1,
        "use_ssl": False
    },
    {
        "name": "24-port Switch",
        "ip_address": "192.168.100.3",
        "port": 8728,
        "username": "admin",
        "password": "Dragon@123!@#",
        "device_type": "switch",
        "model": "CRS226-24G-2S+",
        "site_id": 1,
        "use_ssl": False
    }
]


def create_device(device_data):
    """Create a device via API"""
    print(f"\nAdding device: {device_data['name']} ({device_data['ip_address']})")
    
    try:
        response = requests.post(
            f"{API_BASE}/api/v1/devices",
            json=device_data
        )
        
        if response.status_code == 201:
            device = response.json()
            print(f"✅ Successfully added {device['name']}")
            print(f"   - ID: {device['id']}")
            print(f"   - Model: {device['model']}")
            print(f"   - Status: {'Online' if device['is_online'] else 'Offline'}")
            return device
        else:
            print(f"❌ Failed to add device: {response.status_code}")
            print(f"   Error: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return None


def main():
    print("="*60)
    print("MTCloud Device Seeder")
    print("="*60)
    
    # Check if API is running
    try:
        response = requests.get(f"{API_BASE}/health")
        if response.status_code != 200:
            print("❌ API is not responding correctly")
            sys.exit(1)
        print("✅ API is running")
    except Exception as e:
        print(f"❌ Cannot connect to API: {str(e)}")
        print("Make sure the backend server is running on port 8001")
        sys.exit(1)
    
    # Create all devices
    created = []
    for device_data in DEVICES:
        device = create_device(device_data)
        if device:
            created.append(device)
    
    print("\n" + "="*60)
    print(f"Summary: {len(created)}/{len(DEVICES)} devices added successfully")
    print("="*60)
    
    if created:
        print("\nDevices in database:")
        for device in created:
            print(f"  • {device['name']} - {device['ip_address']}")


if __name__ == "__main__":
    main()
