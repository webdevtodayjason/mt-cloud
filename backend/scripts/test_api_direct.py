#!/usr/bin/env python3
"""Quick API authentication test"""
import sys
from pathlib import Path

backend_path = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_path))

import routeros_api

# Test connection with detailed error output
try:
    print("Attempting to connect to 192.168.100.1...")
    print("Using plaintext_login=True")
    
    connection = routeros_api.RouterOsApiPool(
        host='192.168.100.1',
        username='admin',
        password='Dragon@123!@#',
        port=8728,
        use_ssl=False,
        plaintext_login=True
    )
    
    api = connection.get_api()
    print("✅ Connection successful!")
    
    # Try to get system identity
    resource = api.get_resource('/system/identity')
    identity = resource.get()
    print(f"Device identity: {identity}")
    
    connection.disconnect()
    
except Exception as e:
    print(f"❌ Connection failed: {e}")
    print(f"Error type: {type(e).__name__}")
    
    # Try without plaintext_login
    print("\nTrying without plaintext_login flag...")
    try:
        connection = routeros_api.RouterOsApiPool(
            host='192.168.100.1',
            username='admin',
            password='Dragon@123!@#',
            port=8728,
            use_ssl=False
        )
        api = connection.get_api()
        print("✅ Connection successful without plaintext_login!")
        
        resource = api.get_resource('/system/identity')
        identity = resource.get()
        print(f"Device identity: {identity}")
        
        connection.disconnect()
    except Exception as e2:
        print(f"❌ Also failed: {e2}")
