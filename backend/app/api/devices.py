"""
Device management API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional
from datetime import datetime

from app.core.database import get_db
from app.models.device import Device
from app.schemas.device import (
    DeviceCreate,
    DeviceUpdate,
    DeviceResponse,
    DeviceListResponse,
    DeviceTestConnectionResponse
)
from app.services.mikrotik import MikroTikService, MikroTikConnectionError
from cryptography.fernet import Fernet
import os

router = APIRouter(prefix="/api/v1/devices", tags=["devices"])

# Encryption key for device passwords (should be in env var in production)
ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY", Fernet.generate_key())
cipher = Fernet(ENCRYPTION_KEY)


def encrypt_password(password: str) -> str:
    """Encrypt device password"""
    return cipher.encrypt(password.encode()).decode()


def decrypt_password(encrypted: str) -> str:
    """Decrypt device password"""
    return cipher.decrypt(encrypted.encode()).decode()


@router.post("", response_model=DeviceResponse, status_code=201)
async def create_device(
    device_data: DeviceCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new MikroTik device
    
    - **name**: Device name/identifier
    - **ip_address**: Device IP address
    - **port**: RouterOS API port (default: 8728)
    - **username**: RouterOS username
    - **password**: RouterOS password (will be encrypted)
    - **device_type**: Device type (router, switch, access_point, other)
    - **model**: Device model (optional)
    - **site_id**: Site ID this device belongs to
    """
    # Check if device with same IP already exists
    existing = db.query(Device).filter(Device.ip_address == device_data.ip_address).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"Device with IP {device_data.ip_address} already exists")
    
    # Test connection to device before adding
    try:
        mt_service = MikroTikService(
            host=device_data.ip_address,
            username=device_data.username,
            password=device_data.password,
            port=device_data.port,
            use_ssl=device_data.use_ssl
        )
        connection_result = mt_service.test_connection()
        
        if not connection_result['success']:
            raise HTTPException(
                status_code=400,
                detail=f"Cannot connect to device: {connection_result.get('error', 'Unknown error')}"
            )
        
        # Create device record with info from MikroTik
        device = Device(
            name=device_data.name,
            ip_address=device_data.ip_address,
            port=device_data.port,
            username=device_data.username,
            encrypted_password=encrypt_password(device_data.password),
            device_type=device_data.device_type.value,
            model=device_data.model or connection_result.get('platform'),
            serial_number=None,  # TODO: Extract from device
            firmware_version=connection_result.get('version'),
            is_online=True,
            last_seen=datetime.utcnow(),
            site_id=device_data.site_id
        )
        
        db.add(device)
        db.commit()
        db.refresh(device)
        
        return device
        
    except MikroTikConnectionError as e:
        raise HTTPException(status_code=400, detail=f"Connection failed: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create device: {str(e)}")


@router.get("", response_model=DeviceListResponse)
async def list_devices(
    site_id: Optional[int] = Query(None, description="Filter by site ID"),
    device_type: Optional[str] = Query(None, description="Filter by device type"),
    is_online: Optional[bool] = Query(None, description="Filter by online status"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db)
):
    """
    List all devices with optional filtering and pagination
    
    - **site_id**: Filter devices by site
    - **device_type**: Filter by device type
    - **is_online**: Filter by online status
    - **page**: Page number (starts at 1)
    - **page_size**: Number of items per page
    """
    query = db.query(Device)
    
    # Apply filters
    if site_id is not None:
        query = query.filter(Device.site_id == site_id)
    if device_type:
        query = query.filter(Device.device_type == device_type)
    if is_online is not None:
        query = query.filter(Device.is_online == is_online)
    
    # Get total count
    total = query.count()
    
    # Apply pagination
    offset = (page - 1) * page_size
    devices = query.offset(offset).limit(page_size).all()
    
    return DeviceListResponse(
        total=total,
        devices=devices,
        page=page,
        page_size=page_size
    )


@router.get("/{device_id}", response_model=DeviceResponse)
async def get_device(
    device_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific device by ID"""
    device = db.query(Device).filter(Device.id == device_id).first()
    if not device:
        raise HTTPException(status_code=404, detail=f"Device {device_id} not found")
    return device


@router.put("/{device_id}", response_model=DeviceResponse)
async def update_device(
    device_id: int,
    device_data: DeviceUpdate,
    db: Session = Depends(get_db)
):
    """
    Update a device's information
    
    Only provided fields will be updated.
    """
    device = db.query(Device).filter(Device.id == device_id).first()
    if not device:
        raise HTTPException(status_code=404, detail=f"Device {device_id} not found")
    
    # Update fields if provided
    update_data = device_data.model_dump(exclude_unset=True)
    
    # Encrypt password if being updated
    if 'password' in update_data:
        update_data['encrypted_password'] = encrypt_password(update_data.pop('password'))
    
    # Convert device_type enum to string if present
    if 'device_type' in update_data and update_data['device_type']:
        update_data['device_type'] = update_data['device_type'].value
    
    for field, value in update_data.items():
        setattr(device, field, value)
    
    device.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(device)
    
    return device


@router.delete("/{device_id}", status_code=204)
async def delete_device(
    device_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete a device
    
    This will also delete all associated metrics, interfaces, and configurations.
    """
    device = db.query(Device).filter(Device.id == device_id).first()
    if not device:
        raise HTTPException(status_code=404, detail=f"Device {device_id} not found")
    
    db.delete(device)
    db.commit()
    
    return None


@router.post("/{device_id}/test", response_model=DeviceTestConnectionResponse)
async def test_device_connection(
    device_id: int,
    db: Session = Depends(get_db)
):
    """
    Test connection to a device
    
    Attempts to connect to the device and retrieve basic information.
    Updates device status if successful.
    """
    device = db.query(Device).filter(Device.id == device_id).first()
    if not device:
        raise HTTPException(status_code=404, detail=f"Device {device_id} not found")
    
    try:
        # Decrypt password
        password = decrypt_password(device.encrypted_password)
        
        # Test connection
        mt_service = MikroTikService(
            host=device.ip_address,
            username=device.username,
            password=password,
            port=device.port
        )
        
        result = mt_service.test_connection()
        
        # Update device status
        device.is_online = result['success']
        device.last_seen = datetime.utcnow()
        
        if result['success']:
            device.firmware_version = result.get('version')
            device.model = result.get('platform')
        
        db.commit()
        
        return DeviceTestConnectionResponse(
            success=result['success'],
            message="Connection successful" if result['success'] else "Connection failed",
            device_info=result if result['success'] else None,
            error=result.get('error') if not result['success'] else None
        )
        
    except Exception as e:
        device.is_online = False
        db.commit()
        
        return DeviceTestConnectionResponse(
            success=False,
            message="Connection test failed",
            error=str(e)
        )


@router.get("/{device_id}/status")
async def get_device_status(
    device_id: int,
    db: Session = Depends(get_db)
):
    """
    Get quick device status (online/offline, last seen, uptime)
    """
    device = db.query(Device).filter(Device.id == device_id).first()
    if not device:
        raise HTTPException(status_code=404, detail=f"Device {device_id} not found")
    
    return {
        "id": device.id,
        "name": device.name,
        "ip_address": device.ip_address,
        "is_online": device.is_online,
        "last_seen": device.last_seen,
        "firmware_version": device.firmware_version
    }
