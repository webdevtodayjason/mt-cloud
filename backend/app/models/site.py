from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class Site(Base):
    """
    Physical locations for each client
    E.g., Round Rock Office, North Austin Office for D Fox Law
    """
    __tablename__ = "sites"

    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("clients.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Site information
    name = Column(String(255), nullable=False)
    slug = Column(String(100), nullable=False, index=True)
    
    # Address
    address_line1 = Column(String(255))
    address_line2 = Column(String(255))
    city = Column(String(100))
    state = Column(String(50))
    zip_code = Column(String(20))
    country = Column(String(100), default="USA")
    
    # Geographic coordinates
    latitude = Column(Numeric(precision=10, scale=7))
    longitude = Column(Numeric(precision=10, scale=7))
    
    # Configuration
    timezone = Column(String(50), default="America/Chicago")
    
    # Contact
    site_contact_name = Column(String(255))
    site_contact_phone = Column(String(50))
    site_contact_email = Column(String(255))
    
    # Notes
    notes = Column(Text)
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    client = relationship("Client", back_populates="sites")
    devices = relationship("Device", back_populates="site", cascade="all, delete-orphan")
    device_groups = relationship("DeviceGroup", back_populates="site", cascade="all, delete-orphan")
    ai_insights = relationship("AIInsight", back_populates="site")

    def __repr__(self):
        return f"<Site {self.name}>"
