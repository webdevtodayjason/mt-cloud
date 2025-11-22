#!/bin/bash
# Script to check if MikroTik API service is enabled and running

echo "=============================================="
echo "MikroTik API Service Status Check"
echo "=============================================="
echo ""

devices=(
    "192.168.100.1:Main Router (CRS310)"
    "192.168.100.2:10G Switch (CRS309)"
    "192.168.100.3:24-port Switch (CRS226)"
)

echo "This script will check if the RouterOS API service is enabled on your devices."
echo ""
read -p "Enter admin username (default: admin): " username
username=${username:-admin}

echo ""

for device_info in "${devices[@]}"; do
    IFS=':' read -r ip name <<< "$device_info"
    
    echo "=============================================="
    echo "Checking: $name"
    echo "IP: $ip"
    echo "=============================================="
    
    # Check API service status
    echo ""
    echo "API Service Status:"
    ssh -o ConnectTimeout=5 "${username}@${ip}" "/ip service print detail where name=api" 2>&1
    
    if [ $? -eq 0 ]; then
        echo ""
        echo "✅ Successfully connected to $name"
        echo ""
        echo "To enable API if disabled, run:"
        echo "  ssh ${username}@${ip}"
        echo "  /ip service enable api"
    else
        echo ""
        echo "❌ Could not connect to $name"
        echo "Check if:"
        echo "  1. Device is online and reachable"
        echo "  2. SSH service is enabled"
        echo "  3. Credentials are correct"
    fi
    
    echo ""
done

echo "=============================================="
echo "API Port Information:"
echo "=============================================="
echo "Default API ports:"
echo "  - API (unencrypted):  8728"
echo "  - API-SSL (encrypted): 8729"
echo ""
echo "To enable API service on a device, SSH in and run:"
echo "  /ip service enable api"
echo "  /ip service set api address=192.168.100.0/24"
echo ""
echo "To enable API-SSL (recommended):"
echo "  /ip service enable api-ssl"
echo "  /ip service set api-ssl address=192.168.100.0/24"
echo "=============================================="
