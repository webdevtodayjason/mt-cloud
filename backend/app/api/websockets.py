"""
WebSocket endpoints for real-time metrics streaming
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.orm import Session
from typing import Dict, Set
import asyncio
import json
from datetime import datetime

from app.core.database import get_db
from app.models.device import Device
from app.services.mikrotik import MikroTikService
from app.api.devices import decrypt_password

router = APIRouter(tags=["websockets"])


class ConnectionManager:
    """Manages WebSocket connections for real-time metrics"""
    
    def __init__(self):
        self.active_connections: Dict[int, Set[WebSocket]] = {}
    
    async def connect(self, device_id: int, websocket: WebSocket):
        """Accept and register a new WebSocket connection"""
        await websocket.accept()
        if device_id not in self.active_connections:
            self.active_connections[device_id] = set()
        self.active_connections[device_id].add(websocket)
    
    def disconnect(self, device_id: int, websocket: WebSocket):
        """Remove a WebSocket connection"""
        if device_id in self.active_connections:
            self.active_connections[device_id].discard(websocket)
            if not self.active_connections[device_id]:
                del self.active_connections[device_id]
    
    async def broadcast(self, device_id: int, message: dict):
        """Broadcast message to all connections for a device"""
        if device_id in self.active_connections:
            dead_connections = set()
            for connection in self.active_connections[device_id]:
                try:
                    await connection.send_json(message)
                except:
                    dead_connections.add(connection)
            
            # Clean up dead connections
            for conn in dead_connections:
                self.disconnect(device_id, conn)


manager = ConnectionManager()


async def fetch_device_metrics(device: Device):
    """Fetch current metrics from a device"""
    try:
        password = decrypt_password(device.encrypted_password)
        
        with MikroTikService(
            host=device.ip_address,
            username=device.username,
            password=password,
            port=device.port
        ) as mt:
            resources = mt.get_system_resources()
            interfaces = mt.get_interfaces()
            
            # Parse system metrics
            free_memory = int(resources.get('free-memory', 0))
            total_memory = int(resources.get('total-memory', 0))
            
            return {
                "timestamp": datetime.utcnow().isoformat(),
                "device_id": device.id,
                "device_name": device.name,
                "system": {
                    "cpu_load": int(resources.get('cpu-load', 0)),
                    "memory_used": total_memory - free_memory,
                    "memory_total": total_memory,
                    "memory_percent": round((total_memory - free_memory) / total_memory * 100, 1) if total_memory > 0 else 0,
                    "uptime": resources.get('uptime', 'Unknown'),
                    "version": resources.get('version', 'Unknown')
                },
                "interfaces": [
                    {
                        "name": iface.get('name'),
                        "rx_bytes": int(iface.get('rx-byte', 0)),
                        "tx_bytes": int(iface.get('tx-byte', 0)),
                        "rx_packets": int(iface.get('rx-packet', 0)),
                        "tx_packets": int(iface.get('tx-packet', 0))
                    }
                    for iface in interfaces[:10]  # Limit to first 10 interfaces
                ],
                "status": "online"
            }
    except Exception as e:
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "device_id": device.id,
            "device_name": device.name,
            "status": "error",
            "error": str(e)
        }


@router.websocket("/ws/devices/{device_id}/live")
async def websocket_device_metrics(
    websocket: WebSocket,
    device_id: int
):
    """
    WebSocket endpoint for streaming real-time device metrics
    
    Sends metrics every 3 seconds for the specified device
    """
    # Get database session
    db = next(get_db())
    
    try:
        # Check if device exists
        device = db.query(Device).filter(Device.id == device_id).first()
        if not device:
            await websocket.close(code=1008, reason="Device not found")
            return
        
        # Accept connection
        await manager.connect(device_id, websocket)
        
        # Send initial message
        await websocket.send_json({
            "type": "connected",
            "device_id": device_id,
            "device_name": device.name,
            "message": "Connected to device metrics stream"
        })
        
        # Stream metrics loop
        while True:
            try:
                # Fetch current metrics
                metrics = await fetch_device_metrics(device)
                
                # Send to client
                await websocket.send_json({
                    "type": "metrics",
                    **metrics
                })
                
                # Wait 3 seconds before next update
                await asyncio.sleep(3)
                
            except WebSocketDisconnect:
                break
            except Exception as e:
                # Send error but continue
                await websocket.send_json({
                    "type": "error",
                    "message": str(e),
                    "timestamp": datetime.utcnow().isoformat()
                })
                await asyncio.sleep(3)
    
    finally:
        manager.disconnect(device_id, websocket)
        db.close()


@router.websocket("/ws/dashboard")
async def websocket_dashboard(websocket: WebSocket):
    """
    WebSocket endpoint for dashboard overview
    
    Streams summary metrics for all devices
    """
    db = next(get_db())
    
    try:
        await websocket.accept()
        
        await websocket.send_json({
            "type": "connected",
            "message": "Connected to dashboard stream"
        })
        
        while True:
            try:
                # Get all devices
                devices = db.query(Device).all()
                
                # Collect summary data
                summary = {
                    "type": "dashboard",
                    "timestamp": datetime.utcnow().isoformat(),
                    "total_devices": len(devices),
                    "online_devices": sum(1 for d in devices if d.is_online),
                    "offline_devices": sum(1 for d in devices if not d.is_online),
                    "devices": [
                        {
                            "id": d.id,
                            "name": d.name,
                            "ip_address": d.ip_address,
                            "is_online": d.is_online,
                            "device_type": d.device_type,
                            "model": d.model,
                            "last_seen": d.last_seen.isoformat() if d.last_seen else None
                        }
                        for d in devices
                    ]
                }
                
                await websocket.send_json(summary)
                
                # Update every 5 seconds
                await asyncio.sleep(5)
                
            except WebSocketDisconnect:
                break
            except Exception as e:
                await websocket.send_json({
                    "type": "error",
                    "message": str(e)
                })
                await asyncio.sleep(5)
    
    finally:
        db.close()
