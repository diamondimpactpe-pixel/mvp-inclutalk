"""
Session model - represents individual service desk attention sessions
"""
from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Session(Base):
    """Session model for tracking service desk interactions"""
    __tablename__ = "sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    institution_id = Column(Integer, ForeignKey("institutions.id", ondelete="CASCADE"), nullable=False)
    operator_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    
    # Session metadata
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    ended_at = Column(DateTime(timezone=True), nullable=True)
    
    # Metrics (collected if COLLECT_METRICS=True)
    turns_count = Column(Integer, default=0)  # Number of interaction turns
    stt_attempts = Column(Integer, default=0)  # Voice to text attempts
    lsp_attempts = Column(Integer, default=0)  # Sign language attempts
    lsp_failed_attempts = Column(Integer, default=0)  # Failed sign recognition
    text_fallback_count = Column(Integer, default=0)  # Times user wrote instead
    avg_confidence = Column(Float, default=0.0)  # Average LSP confidence
    total_duration_seconds = Column(Integer, default=0)  # Session duration
    
    # Optional notes (not conversation text for privacy)
    operator_notes = Column(Text, nullable=True)
    
    # Relationships
    institution = relationship("Institution", back_populates="sessions")
    operator = relationship("User", back_populates="sessions")
    
    def __repr__(self):
        return f"<Session {self.id} - Institution {self.institution_id}>"
    
    @property
    def duration_minutes(self):
        """Calculate duration in minutes"""
        if self.total_duration_seconds:
            return round(self.total_duration_seconds / 60, 2)
        return 0
    
    @property
    def is_active(self):
        """Check if session is still active"""
        return self.ended_at is None
