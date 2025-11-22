from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class Client(Base):
    """
    Customer companies under an MSP organization
    E.g., D Fox Law, Christiansen Plumbing under Titanium Computing
    """
    __tablename__ = "clients"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Client information
    name = Column(String(255), nullable=False)
    slug = Column(String(100), nullable=False, index=True)
    
    # Contact details
    contact_name = Column(String(255))
    contact_email = Column(String(255))
    contact_phone = Column(String(50))
    
    # Billing
    billing_email = Column(String(255))
    billing_address = Column(Text)
    billing_contact = Column(String(255))
    
    # Notes and metadata
    notes = Column(Text)
    industry = Column(String(100))  # Legal, Plumbing, Retail, etc.
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    organization = relationship("Organization", back_populates="clients")
    sites = relationship("Site", back_populates="client", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Client {self.name}>"
