from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, Float, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class Alert(Base):
    """
    Alert rules/definitions for monitoring
    """
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    device_id = Column(Integer, ForeignKey("devices.id", ondelete="CASCADE"), index=True)  # Optional, can be site-wide
    site_id = Column(Integer, ForeignKey("sites.id", ondelete="CASCADE"), index=True)  # Optional
    
    # Alert configuration
    name = Column(String(255), nullable=False)
    description = Column(Text)
    
    # Condition
    metric_type = Column(String(100), nullable=False)  # cpu_load, memory_usage, interface_down, etc.
    condition = Column(String(50), nullable=False)  # greater_than, less_than, equals, not_equals
    threshold = Column(Float, nullable=False)
    duration_seconds = Column(Integer, default=0)  # Alert only if condition persists for X seconds
    
    # Severity
    severity = Column(String(50), default="warning")  # info, warning, error, critical
    
    # Notification settings
    notify_users = Column(JSON, default=[])  # Array of user IDs to notify
    notify_email = Column(String(255))  # Additional email address
    notify_webhook = Column(String(500))  # Webhook URL
    
    # Status
    is_enabled = Column(Boolean, default=True, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    organization = relationship("Organization", back_populates="alerts")
    history = relationship("AlertHistory", back_populates="alert", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Alert {self.name} ({self.metric_type} {self.condition} {self.threshold})>"


class AlertHistory(Base):
    """
    History of triggered alerts
    """
    __tablename__ = "alert_history"

    id = Column(Integer, primary_key=True, index=True)
    alert_id = Column(Integer, ForeignKey("alerts.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Alert trigger details
    value = Column(Float, nullable=False)  # The value that triggered the alert
    message = Column(Text)
    
    # Status
    is_acknowledged = Column(Boolean, default=False)
    acknowledged_at = Column(DateTime(timezone=True))
    acknowledged_by_user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    
    resolved_at = Column(DateTime(timezone=True))
    
    # Timestamps
    triggered_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    
    # Relationships
    alert = relationship("Alert", back_populates="history")

    def __repr__(self):
        return f"<AlertHistory alert_{self.alert_id} triggered at {self.triggered_at}>"
