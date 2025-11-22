from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


# Association table for many-to-many relationship between devices and groups
device_group_members = Table(
    'device_group_members',
    Base.metadata,
    Column('device_id', Integer, ForeignKey('devices.id', ondelete='CASCADE'), primary_key=True),
    Column('group_id', Integer, ForeignKey('device_groups.id', ondelete='CASCADE'), primary_key=True)
)


class Device(Base):
    """
    MikroTik network devices (routers, switches, access points)
    """
    __tablename__ = "devices"

    id = Column(Integer, primary_key=True, index=True)
    site_id = Column(Integer, ForeignKey("sites.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Device identification
    name = Column(String(255), nullable=False)
    hostname = Column(String(255))
    ip_address = Column(String(45), nullable=False)  # Supports IPv6
    port = Column(Integer, default=8728)
    
    # Device type and model
    device_type = Column(String(50), nullable=False)  # router, switch, access_point, other
    model = Column(String(100))  # e.g., "hEX S", "CRS328-24P-4S+RM"
    serial_number = Column(String(100))
    mac_address = Column(String(17))
    
    # RouterOS information
    routeros_version = Column(String(50))
    firmware_version = Column(String(50))
    architecture = Column(String(50))  # mipsbe, arm, tile, etc.
    
    # Credentials (encrypted)
    username = Column(String(255), nullable=False)
    encrypted_password = Column(Text, nullable=False)
    use_ssl = Column(Boolean, default=True)
    
    # Status and health
    is_online = Column(Boolean, default=False)
    is_monitored = Column(Boolean, default=True)
    last_seen_at = Column(DateTime(timezone=True))
    last_poll_at = Column(DateTime(timezone=True))
    uptime_seconds = Column(Integer)
    
    # Resource usage (cached from last poll)
    cpu_load_percent = Column(Integer)
    memory_total_bytes = Column(Integer)
    memory_used_bytes = Column(Integer)
    disk_total_bytes = Column(Integer)
    disk_used_bytes = Column(Integer)
    
    # Configuration
    notes = Column(Text)
    polling_interval_seconds = Column(Integer, default=60)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    site = relationship("Site", back_populates="devices")
    interfaces = relationship("Interface", back_populates="device", cascade="all, delete-orphan")
    metrics = relationship("DeviceMetric", back_populates="device", cascade="all, delete-orphan")
    configs = relationship("DeviceConfig", back_populates="device", cascade="all, delete-orphan")
    groups = relationship("DeviceGroup", secondary=device_group_members, back_populates="devices")

    def __repr__(self):
        return f"<Device {self.name} ({self.ip_address})>"


class DeviceGroup(Base):
    """
    Logical grouping of devices within a site
    E.g., "Edge Routers", "Core Switches", "WiFi APs"
    """
    __tablename__ = "device_groups"

    id = Column(Integer, primary_key=True, index=True)
    site_id = Column(Integer, ForeignKey("sites.id", ondelete="CASCADE"), nullable=False, index=True)
    
    name = Column(String(255), nullable=False)
    description = Column(Text)
    color = Column(String(7))  # Hex color for UI
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    site = relationship("Site", back_populates="device_groups")
    devices = relationship("Device", secondary=device_group_members, back_populates="groups")

    def __repr__(self):
        return f"<DeviceGroup {self.name}>"


class DeviceConfig(Base):
    """
    Configuration backups for devices
    """
    __tablename__ = "device_configs"

    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(Integer, ForeignKey("devices.id", ondelete="CASCADE"), nullable=False, index=True)
    
    config_data = Column(Text, nullable=False)
    backup_type = Column(String(50), default="manual")  # manual, automatic, scheduled
    file_size_bytes = Column(Integer)
    
    created_by_user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    device = relationship("Device", back_populates="configs")

    def __repr__(self):
        return f"<DeviceConfig for device_{self.device_id} at {self.created_at}>"
