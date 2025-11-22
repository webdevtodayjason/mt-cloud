from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from pgvector.sqlalchemy import Vector
from app.core.database import Base


class AIInsight(Base):
    """
    AI-generated insights and reports with vector embeddings for semantic search
    """
    __tablename__ = "ai_insights"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    site_id = Column(Integer, ForeignKey("sites.id", ondelete="CASCADE"), index=True)  # Optional
    
    # Insight type and content
    insight_type = Column(String(100), nullable=False)  # daily_summary, anomaly_detection, prediction, recommendation
    summary = Column(Text, nullable=False)
    details_json = Column(JSON)  # Structured data about the insight
    
    # Severity/importance
    severity = Column(String(50), default="info")  # info, warning, critical
    priority_score = Column(Integer, default=0)  # 0-100
    
    # AI metadata
    ai_model = Column(String(100))  # gpt-4, claude-3-sonnet, etc.
    tokens_used = Column(Integer)
    generation_time_ms = Column(Integer)
    
    # Vector embedding for semantic search (1536 dimensions for OpenAI embeddings)
    embedding = Column(Vector(1536))
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    
    # Relationships
    organization = relationship("Organization", back_populates="ai_insights")
    site = relationship("Site", back_populates="ai_insights")

    def __repr__(self):
        return f"<AIInsight {self.insight_type} for org_{self.organization_id}>"


class AIQuery(Base):
    """
    User AI query history with embeddings for context
    """
    __tablename__ = "ai_queries"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Query and response
    query_text = Column(Text, nullable=False)
    response_text = Column(Text, nullable=False)
    
    # Context
    context_json = Column(JSON)  # Additional context (e.g., selected devices, date range)
    
    # AI metadata
    ai_provider = Column(String(50))  # openai, anthropic, xai, local
    ai_model = Column(String(100))
    tokens_used = Column(Integer)
    response_time_ms = Column(Integer)
    
    # Vector embedding for semantic search
    embedding = Column(Vector(1536))
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    
    # Relationships
    user = relationship("User", back_populates="ai_queries")

    def __repr__(self):
        return f"<AIQuery by user_{self.user_id} at {self.created_at}>"


class MetricEmbedding(Base):
    """
    Vectorized summaries of metrics for RAG-based AI analysis
    """
    __tablename__ = "metric_embeddings"

    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(Integer, ForeignKey("devices.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Time period this embedding represents
    time_period_start = Column(DateTime(timezone=True), nullable=False, index=True)
    time_period_end = Column(DateTime(timezone=True), nullable=False)
    
    # Summary text and metadata
    summary_text = Column(Text, nullable=False)
    metrics_json = Column(JSON)  # Aggregated metrics for this period
    
    # Vector embedding
    embedding = Column(Vector(1536))
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    def __repr__(self):
        return f"<MetricEmbedding device_{self.device_id} {self.time_period_start} to {self.time_period_end}>"
