from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class User(Base):
    """
    Platform users with role-based access control
    Roles: global_admin, msp_admin, client_admin, technician, viewer
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Authentication
    email = Column(String(255), nullable=False, unique=True, index=True)
    password_hash = Column(String(255), nullable=False)
    
    # Profile
    first_name = Column(String(100))
    last_name = Column(String(100))
    phone = Column(String(50))
    avatar_url = Column(String(500))
    
    # Role-based access
    role = Column(String(50), nullable=False, default="viewer")  # global_admin, msp_admin, client_admin, technician, viewer
    
    # Client assignments (for client_admin, technician, viewer roles)
    # JSON array of client IDs this user can access
    assigned_client_ids = Column(JSON, default=[])
    
    # Permissions and settings
    can_manage_devices = Column(Boolean, default=False)
    can_view_reports = Column(Boolean, default=True)
    can_manage_alerts = Column(Boolean, default=False)
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    is_email_verified = Column(Boolean, default=False)
    email_verified_at = Column(DateTime(timezone=True))
    
    # Last activity
    last_login_at = Column(DateTime(timezone=True))
    last_login_ip = Column(String(50))
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    organization = relationship("Organization", back_populates="users")
    ai_queries = relationship("AIQuery", back_populates="user")

    def __repr__(self):
        return f"<User {self.email} ({self.role})>"
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip() or self.email
