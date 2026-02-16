"""
Metrics model - aggregated metrics for reporting
"""
from sqlalchemy import Column, Integer, Date, DateTime, Float, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class MetricsDaily(Base):
    """Daily aggregated metrics per institution"""
    __tablename__ = "metrics_daily"
    
    id = Column(Integer, primary_key=True, index=True)
    institution_id = Column(Integer, ForeignKey("institutions.id", ondelete="CASCADE"), nullable=False)
    date = Column(Date, nullable=False, index=True)
    
    # Session metrics
    sessions_count = Column(Integer, default=0)
    avg_duration_minutes = Column(Float, default=0.0)
    total_turns = Column(Integer, default=0)
    
    # LSP metrics
    lsp_total_attempts = Column(Integer, default=0)
    lsp_successful_attempts = Column(Integer, default=0)
    lsp_avg_confidence = Column(Float, default=0.0)
    
    # User experience
    text_fallback_count = Column(Integer, default=0)
    avg_turns_per_session = Column(Float, default=0.0)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    institution = relationship("Institution")
    
    def __repr__(self):
        return f"<MetricsDaily {self.date} - Institution {self.institution_id}>"
    
    @property
    def success_rate(self):
        """Calculate LSP success rate"""
        if self.lsp_total_attempts > 0:
            return round((self.lsp_successful_attempts / self.lsp_total_attempts) * 100, 2)
        return 0.0
