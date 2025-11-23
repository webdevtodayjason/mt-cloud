"""
Pydantic schemas for device API endpoints
"""
from pydantic import BaseModel, Field, IPvAnyAddress
from typing import Optional
from datetime import datetime
from enum import Enum


class DeviceType(str, Enum):
    """Device type enumeration"""
    ROUTER = "router"
    SWITCH = "switch"
    ACCESS_POINT = "access_point"
    OTHER = "other"


class DeviceStatus(str, Enum):
    """Device status enumeration"""
    ONLINE = "online"
    OFFLINE = "offline"
    UNKNOWN = "unknown"


# Request Schemas
class DeviceCreate(BaseModel):
    """Schema for creating a new device"""
    name: str = Field(..., min_length=1, max_length=255, description="Device name")
    ip_address: str = Field(..., description="Device IP address")
    port: int = Field(default=8728, ge=1, le=65535, description="API port")
    username: str = Field(..., min_length=1, description="RouterOS username")
    password: str = Field(..., min_length=1, description="RouterOS password")
    device_type: DeviceType = Field(default=DeviceType.ROUTER, description="Device type")
    model: Optional[str] = Field(None, max_length=255, description="Device model")
    site_id: int = Field(..., description="Site ID this device belongs to")
    use_ssl: bool = Field(default=False, description="Use SSL for API connection")
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "Main Router",
                "ip_address": "192.168.100.1",
                "port": 8728,
                "username": "admin",
                "password": "password123",
                "device_type": "router",
                "model": "CRS310-8G+2S+",
                "site_id": 1,
                "use_ssl": False
            }
        }


class DeviceUpdate(BaseModel):
    """Schema for updating an existing device"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    ip_address: Optional[str] = None
    port: Optional[int] = Field(None, ge=1, le=65535)
    username: Optional[str] = Field(None, min_length=1)
    password: Optional[str] = Field(None, min_length=1)
    device_type: Optional[DeviceType] = None
    model: Optional[str] = Field(None, max_length=255)
    use_ssl: Optional[bool] = None


# Response Schemas
class DeviceResponse(BaseModel):
    """Schema for device response"""
    id: int
    name: str
    ip_address: str
    port: int
    username: str
    device_type: DeviceType
    model: Optional[str]
    serial_number: Optional[str]
    firmware_version: Optional[str]
    is_online: bool
    last_seen_at: Optional[datetime]
    site_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class DeviceListResponse(BaseModel):
    """Schema for paginated device list"""
    total: int
    devices: list[DeviceResponse]
    page: int
    page_size: int


class DeviceTestConnectionResponse(BaseModel):
    """Schema for device connection test result"""
    success: bool
    message: str
    device_info: Optional[dict] = None
    error: Optional[str] = None


# Metrics Schemas
class SystemMetrics(BaseModel):
    """Current system metrics"""
    cpu_load: int = Field(..., ge=0, le=100, description="CPU load percentage")
    memory_used: int = Field(..., description="Used memory in bytes")
    memory_total: int = Field(..., description="Total memory in bytes")
    uptime: str = Field(..., description="System uptime")
    version: str = Field(..., description="RouterOS version")
    board_name: str = Field(..., description="Board/model name")


class InterfaceStats(BaseModel):
    """Interface statistics"""
    name: str
    rx_bytes: int
    tx_bytes: int
    rx_packets: int
    tx_packets: int
    rx_errors: int
    tx_errors: int
    rx_drops: int
    tx_drops: int


class DeviceMetricsResponse(BaseModel):
    """Complete device metrics response"""
    device_id: int
    device_name: str
    system: SystemMetrics
    interfaces: list[InterfaceStats]
    timestamp: datetime


class InterfaceResponse(BaseModel):
    """Interface information"""
    id: int
    device_id: int
    name: str
    mac_address: Optional[str]
    type: str
    speed: Optional[str]
    is_enabled: bool
    
    class Config:
        from_attributes = True


# Historical Data Schemas
class MetricType(str, Enum):
    """Metric type enumeration"""
    CPU = "cpu"
    MEMORY = "memory"
    INTERFACE_RX = "interface_rx"
    INTERFACE_TX = "interface_tx"


class HistoricalMetricsQuery(BaseModel):
    """Query parameters for historical metrics"""
    metric_type: MetricType
    start_time: datetime
    end_time: datetime
    interval: str = Field(default="1h", description="Aggregation interval (1m, 5m, 1h, 1d)")


class HistoricalDataPoint(BaseModel):
    """Single historical data point"""
    timestamp: datetime
    value: float
    

class HistoricalMetricsResponse(BaseModel):
    """Historical metrics response"""
    device_id: int
    metric_type: MetricType
    data_points: list[HistoricalDataPoint]
    start_time: datetime
    end_time: datetime
