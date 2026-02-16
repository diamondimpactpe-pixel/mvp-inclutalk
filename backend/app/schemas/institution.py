"""
Institution schemas
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
from app.models.institution import InstitutionSector


class InstitutionBase(BaseModel):
    """Base institution schema"""
    name: str = Field(..., min_length=3, max_length=255)
    sector: InstitutionSector = InstitutionSector.OTHER
    contact_email: Optional[EmailStr] = None
    contact_phone: Optional[str] = Field(None, max_length=50)


class InstitutionCreate(InstitutionBase):
    """Schema for creating an institution"""
    pass


class InstitutionUpdate(BaseModel):
    """Schema for updating an institution"""
    name: Optional[str] = Field(None, min_length=3, max_length=255)
    sector: Optional[InstitutionSector] = None
    contact_email: Optional[EmailStr] = None
    contact_phone: Optional[str] = Field(None, max_length=50)
    is_active: Optional[int] = Field(None, ge=0, le=1)


class InstitutionResponse(InstitutionBase):
    """Schema for institution response"""
    id: int
    is_active: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    # Computed fields
    active_operators_count: Optional[int] = 0
    active_sessions_count: Optional[int] = 0
    
    class Config:
        from_attributes = True


class InstitutionWithStats(InstitutionResponse):
    """Institution with statistics"""
    total_sessions: int = 0
    avg_session_duration: float = 0.0
    monthly_cost: float = 0.0  # Calculated based on pricing model
    
    class Config:
        from_attributes = True
