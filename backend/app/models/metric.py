from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class DeviceMetric(Base):
    """
    Time-series metrics for devices (CPU, memory, temperature, etc.)
    """
    __tablename__ = "device_metrics"

    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(Integer, ForeignKey("devices.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Metric type and value
    metric_type = Column(String(100), nullable=False, index=True)  # cpu_load, memory_usage, temperature, uptime, etc.
    value = Column(Float, nullable=False)
    unit = Column(String(50))  # percent, bytes, celsius, seconds, etc.
    
    # Timestamp (indexed for time-series queries)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    
    # Relationships
    device = relationship("Device", back_populates="metrics")

    def __repr__(self):
        return f"<DeviceMetric {self.metric_type}={self.value} for device_{self.device_id}>"
