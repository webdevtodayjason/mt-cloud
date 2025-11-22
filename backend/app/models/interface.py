from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, BigInteger
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class Interface(Base):
    """
    Network interfaces on MikroTik devices
    """
    __tablename__ = "interfaces"

    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(Integer, ForeignKey("devices.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Interface information
    name = Column(String(255), nullable=False)  # e.g., "ether1", "wlan1", "bridge"
    mac_address = Column(String(17))
    type = Column(String(50))  # ethernet, wireless, bridge, vlan, etc.
    
    # Status
    is_enabled = Column(Boolean, default=True)
    is_running = Column(Boolean, default=False)
    
    # Configuration
    speed_mbps = Column(Integer)  # Link speed
    mtu = Column(Integer, default=1500)
    
    # Last known state
    rx_rate_bps = Column(BigInteger)  # Current receive rate
    tx_rate_bps = Column(BigInteger)  # Current transmit rate
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    device = relationship("Device", back_populates="interfaces")
    stats = relationship("InterfaceStat", back_populates="interface", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Interface {self.name} on device_{self.device_id}>"


class InterfaceStat(Base):
    """
    Time-series statistics for network interfaces
    """
    __tablename__ = "interface_stats"

    id = Column(Integer, primary_key=True, index=True)
    interface_id = Column(Integer, ForeignKey("interfaces.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Traffic counters
    rx_bytes = Column(BigInteger, nullable=False, default=0)
    tx_bytes = Column(BigInteger, nullable=False, default=0)
    rx_packets = Column(BigInteger, nullable=False, default=0)
    tx_packets = Column(BigInteger, nullable=False, default=0)
    
    # Errors and drops
    rx_errors = Column(BigInteger, default=0)
    tx_errors = Column(BigInteger, default=0)
    rx_drops = Column(BigInteger, default=0)
    tx_drops = Column(BigInteger, default=0)
    
    # Timestamp (indexed for time-series queries)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    
    # Relationships
    interface = relationship("Interface", back_populates="stats")

    def __repr__(self):
        return f"<InterfaceStat interface_{self.interface_id} at {self.timestamp}>"
