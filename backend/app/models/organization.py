from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class Organization(Base):
    """
    Top-level entity representing an MSP or company
    Titanium Computing would be organization #1
    """
    __tablename__ = "organizations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, unique=True)
    slug = Column(String(100), nullable=False, unique=True, index=True)
    
    # Plan and limits
    plan_type = Column(String(50), default="standard")  # free, standard, premium, enterprise
    max_devices = Column(Integer, default=100)
    max_users = Column(Integer, default=10)
    
    # Contact and branding
    contact_email = Column(String(255))
    contact_phone = Column(String(50))
    logo_url = Column(String(500))
    primary_color = Column(String(7))  # Hex color for branding
    
    # Billing
    billing_email = Column(String(255))
    billing_address = Column(Text)
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    clients = relationship("Client", back_populates="organization", cascade="all, delete-orphan")
    users = relationship("User", back_populates="organization")
    alerts = relationship("Alert", back_populates="organization")
    ai_insights = relationship("AIInsight", back_populates="organization")

    def __repr__(self):
        return f"<Organization {self.name}>"
