"""
Metrics and monitoring API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional

from app.core.database import get_db
from app.models.device import Device
from app.schemas.device import DeviceMetricsResponse, SystemMetrics, InterfaceStats
from app.services.mikrotik import MikroTikService
from app.api.devices import decrypt_password

router = APIRouter(prefix="/api/v1/metrics", tags=["metrics"])


@router.get("/devices/{device_id}/current", response_model=DeviceMetricsResponse)
async def get_current_metrics(
    device_id: int,
    db: Session = Depends(get_db)
):
    """
    Get current real-time metrics from a device
    
    Returns:
    - System metrics (CPU, memory, uptime)
    - All interface statistics (rx/tx bytes, packets, errors)
    """
    device = db.query(Device).filter(Device.id == device_id).first()
    if not device:
        raise HTTPException(status_code=404, detail=f"Device {device_id} not found")
    
    try:
        # Decrypt password and connect
        password = decrypt_password(device.encrypted_password)
        
        with MikroTikService(
            host=device.ip_address,
            username=device.username,
            password=password,
            port=device.port
        ) as mt:
            # Get system resources
            resources = mt.get_system_resources()
            
            # Parse memory values
            free_memory = int(resources.get('free-memory', 0))
            total_memory = int(resources.get('total-memory', 0))
            memory_used = total_memory - free_memory
            
            system_metrics = SystemMetrics(
                cpu_load=int(resources.get('cpu-load', 0)),
                memory_used=memory_used,
                memory_total=total_memory,
                uptime=resources.get('uptime', 'Unknown'),
                version=resources.get('version', 'Unknown'),
                board_name=resources.get('board-name', 'Unknown')
            )
            
            # Get interface statistics
            interfaces_data = mt.get_interfaces()
            interface_stats = []
            
            for iface in interfaces_data:
                # Get detailed stats for each interface
                stats = InterfaceStats(
                    name=iface.get('name', 'unknown'),
                    rx_bytes=int(iface.get('rx-byte', 0)),
                    tx_bytes=int(iface.get('tx-byte', 0)),
                    rx_packets=int(iface.get('rx-packet', 0)),
                    tx_packets=int(iface.get('tx-packet', 0)),
                    rx_errors=int(iface.get('rx-error', 0)),
                    tx_errors=int(iface.get('tx-error', 0)),
                    rx_drops=int(iface.get('rx-drop', 0)),
                    tx_drops=int(iface.get('tx-drop', 0))
                )
                interface_stats.append(stats)
            
            return DeviceMetricsResponse(
                device_id=device.id,
                device_name=device.name,
                system=system_metrics,
                interfaces=interface_stats,
                timestamp=datetime.utcnow()
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch metrics: {str(e)}"
        )


@router.get("/devices/{device_id}/interfaces")
async def get_device_interfaces(
    device_id: int,
    db: Session = Depends(get_db)
):
    """Get list of all interfaces on a device"""
    device = db.query(Device).filter(Device.id == device_id).first()
    if not device:
        raise HTTPException(status_code=404, detail=f"Device {device_id} not found")
    
    try:
        password = decrypt_password(device.encrypted_password)
        
        with MikroTikService(
            host=device.ip_address,
            username=device.username,
            password=password,
            port=device.port
        ) as mt:
            interfaces = mt.get_interfaces()
            
            return {
                "device_id": device.id,
                "device_name": device.name,
                "interfaces": [
                    {
                        "name": iface.get('name'),
                        "type": iface.get('type', 'Unknown'),
                        "mac_address": iface.get('mac-address'),
                        "running": iface.get('running') == 'true',
                        "disabled": iface.get('disabled') == 'true',
                        "comment": iface.get('comment', '')
                    }
                    for iface in interfaces
                ]
            }
            
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch interfaces: {str(e)}"
        )


@router.get("/devices/{device_id}/dhcp-leases")
async def get_dhcp_leases(
    device_id: int,
    db: Session = Depends(get_db)
):
    """Get DHCP leases from a device"""
    device = db.query(Device).filter(Device.id == device_id).first()
    if not device:
        raise HTTPException(status_code=404, detail=f"Device {device_id} not found")
    
    try:
        password = decrypt_password(device.encrypted_password)
        
        with MikroTikService(
            host=device.ip_address,
            username=device.username,
            password=password,
            port=device.port
        ) as mt:
            leases = mt.get_dhcp_leases()
            
            return {
                "device_id": device.id,
                "device_name": device.name,
                "leases": [
                    {
                        "address": lease.get('address'),
                        "mac_address": lease.get('mac-address'),
                        "host_name": lease.get('host-name', ''),
                        "status": lease.get('status'),
                        "expires_after": lease.get('expires-after', ''),
                        "comment": lease.get('comment', '')
                    }
                    for lease in leases
                ]
            }
            
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch DHCP leases: {str(e)}"
        )


@router.get("/devices/{device_id}/ip-addresses")
async def get_ip_addresses(
    device_id: int,
    db: Session = Depends(get_db)
):
    """Get configured IP addresses on a device"""
    device = db.query(Device).filter(Device.id == device_id).first()
    if not device:
        raise HTTPException(status_code=404, detail=f"Device {device_id} not found")
    
    try:
        password = decrypt_password(device.encrypted_password)
        
        with MikroTikService(
            host=device.ip_address,
            username=device.username,
            password=password,
            port=device.port
        ) as mt:
            addresses = mt.get_ip_addresses()
            
            return {
                "device_id": device.id,
                "device_name": device.name,
                "addresses": [
                    {
                        "address": addr.get('address'),
                        "network": addr.get('network'),
                        "interface": addr.get('interface'),
                        "disabled": addr.get('disabled') == 'true',
                        "invalid": addr.get('invalid') == 'true',
                        "dynamic": addr.get('dynamic') == 'true',
                        "comment": addr.get('comment', '')
                    }
                    for addr in addresses
                ]
            }
            
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch IP addresses: {str(e)}"
        )


@router.get("/devices/{device_id}/system-identity")
async def get_system_identity(
    device_id: int,
    db: Session = Depends(get_db)
):
    """Get device system identity/hostname"""
    device = db.query(Device).filter(Device.id == device_id).first()
    if not device:
        raise HTTPException(status_code=404, detail=f"Device {device_id} not found")
    
    try:
        password = decrypt_password(device.encrypted_password)
        
        with MikroTikService(
            host=device.ip_address,
            username=device.username,
            password=password,
            port=device.port
        ) as mt:
            identity = mt.get_system_identity()
            
            return {
                "device_id": device.id,
                "identity": identity.get('name', 'Unknown')
            }
            
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch system identity: {str(e)}"
        )
