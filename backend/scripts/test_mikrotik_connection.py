#!/usr/bin/env python3
"""
Test script to verify connections to MikroTik devices
"""
import sys
import os
from pathlib import Path
import json
from getpass import getpass

# Add parent directory to path for imports
backend_path = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_path))

from app.services.mikrotik import MikroTikService


# Your MikroTik devices
DEVICES = [
    {
        "name": "Main Router",
        "model": "CRS310-8G+2S+",
        "ip": "192.168.100.1",
        "description": "8x 2.5G + 2x 10G SFP+"
    },
    {
        "name": "10G Switch",
        "model": "CRS309-1G-8S+",
        "ip": "192.168.100.2",
        "description": "1x 1G + 8x 10G SFP+"
    },
    {
        "name": "24-port Switch",
        "model": "CRS226-24G-2S+",
        "ip": "192.168.100.3",
        "description": "24x 1G + 2x 10G SFP+"
    }
]


def test_single_device(device_info: dict, username: str, password: str) -> dict:
    """Test connection to a single device"""
    print(f"\n{'='*60}")
    print(f"Testing: {device_info['name']} ({device_info['model']})")
    print(f"IP: {device_info['ip']}")
    print(f"Description: {device_info['description']}")
    print(f"{'='*60}\n")
    
    service = MikroTikService(
        host=device_info['ip'],
        username=username,
        password=password
    )
    
    result = service.test_connection()
    
    if result['success']:
        print(f"✅ CONNECTION SUCCESSFUL")
        print(f"\nDevice Information:")
        print(f"  Hostname:     {result['identity']}")
        print(f"  Platform:     {result['platform']}")
        print(f"  RouterOS:     {result['version']}")
        print(f"  Uptime:       {result['uptime']}")
        print(f"  CPU Load:     {result['cpu_load']}%")
        
        # Convert memory to GB (handle both int and string values)
        try:
            free_mem = int(result['free_memory']) if isinstance(result['free_memory'], str) else result['free_memory']
            total_mem = int(result['total_memory']) if isinstance(result['total_memory'], str) else result['total_memory']
            free_gb = free_mem / (1024**3)
            total_gb = total_mem / (1024**3)
            used_gb = total_gb - free_gb
            memory_pct = (used_gb / total_gb) * 100
            print(f"  Memory:       {used_gb:.2f} GB / {total_gb:.2f} GB ({memory_pct:.1f}% used)")
        except (ValueError, KeyError, TypeError):
            print(f"  Memory:       {result.get('free_memory', 'N/A')} / {result.get('total_memory', 'N/A')}")
    else:
        print(f"❌ CONNECTION FAILED")
        print(f"Error: {result['error']}")
    
    return result


def main():
    """Main test function"""
    print("="*60)
    print("MikroTik Device Connection Test")
    print("="*60)
    print(f"\nFound {len(DEVICES)} devices to test")
    
    # Use credentials directly for automated testing
    username = "admin"
    password = "Dragon@123!@#"
    
    print(f"\nUsing credentials: {username} / {'*' * len(password)}")
    
    # Test all devices
    results = []
    for device in DEVICES:
        result = test_single_device(device, username, password)
        results.append({
            **device,
            **result
        })
    
    # Summary
    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}\n")
    
    successful = [r for r in results if r['success']]
    failed = [r for r in results if not r['success']]
    
    print(f"✅ Successful: {len(successful)}/{len(DEVICES)}")
    if successful:
        for r in successful:
            print(f"   • {r['name']} ({r['ip']}) - {r['identity']}")
    
    if failed:
        print(f"\n❌ Failed: {len(failed)}/{len(DEVICES)}")
        for r in failed:
            print(f"   • {r['name']} ({r['ip']}) - {r['error']}")
    
    # Save results to JSON
    output_file = backend_path / "scripts" / "test_results.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\n📄 Full results saved to: {output_file}")
    
    # Exit with appropriate code
    sys.exit(0 if len(failed) == 0 else 1)


if __name__ == "__main__":
    main()
