"""
Institution model - represents B2B client organizations
"""
from sqlalchemy import Column, Integer, String, DateTime, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import enum


class InstitutionSector(str, enum.Enum):
    """Enum for institution sectors"""
    GOVERNMENT = "government"
    HEALTHCARE = "healthcare"
    EDUCATION = "education"
    FINANCE = "finance"
    RETAIL = "retail"
    OTHER = "other"


class Institution(Base):
    """Institution model for multi-tenant architecture"""
    __tablename__ = "institutions"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, unique=True, index=True)
    sector = Column(SQLEnum(InstitutionSector), default=InstitutionSector.OTHER)
    contact_email = Column(String(255), nullable=True)
    contact_phone = Column(String(50), nullable=True)
    is_active = Column(Integer, default=1)  # 1 = active, 0 = inactive
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    users = relationship("User", back_populates="institution", cascade="all, delete-orphan")
    sessions = relationship("Session", back_populates="institution", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Institution {self.name}>"
