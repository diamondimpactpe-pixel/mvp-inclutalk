"""
Session schemas
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class SessionCreate(BaseModel):
    """Schema for creating a session"""
    operator_notes: Optional[str] = Field(None, max_length=1000)


class SessionUpdate(BaseModel):
    """Schema for updating session metrics"""
    turns_count: Optional[int] = Field(None, ge=0)
    stt_attempts: Optional[int] = Field(None, ge=0)
    lsp_attempts: Optional[int] = Field(None, ge=0)
    lsp_failed_attempts: Optional[int] = Field(None, ge=0)
    text_fallback_count: Optional[int] = Field(None, ge=0)
    avg_confidence: Optional[float] = Field(None, ge=0.0, le=1.0)
    operator_notes: Optional[str] = Field(None, max_length=1000)


class SessionEnd(BaseModel):
    """Schema for ending a session"""
    operator_notes: Optional[str] = Field(None, max_length=1000)


class SessionResponse(BaseModel):
    """Schema for session response"""
    id: int
    institution_id: int
    operator_id: Optional[int] = None
    started_at: datetime
    ended_at: Optional[datetime] = None
    turns_count: int
    stt_attempts: int
    lsp_attempts: int
    lsp_failed_attempts: int
    text_fallback_count: int
    avg_confidence: float
    total_duration_seconds: int
    is_active: bool
    duration_minutes: float
    
    class Config:
        from_attributes = True


class SessionWithDetails(SessionResponse):
    """Session with operator and institution details"""
    operator_name: Optional[str] = None
    institution_name: str
    
    class Config:
        from_attributes = True


class SessionStats(BaseModel):
    """Session statistics"""
    total_sessions: int
    active_sessions: int
    avg_duration_minutes: float
    avg_turns_per_session: float
    lsp_success_rate: float
    total_text_fallbacks: int
