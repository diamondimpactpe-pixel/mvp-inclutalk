"""
User schemas
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
from app.models.user import UserRole


class UserBase(BaseModel):
    """Base user schema"""
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=100)
    role: UserRole = UserRole.OPERATOR
    first_name: Optional[str] = Field(None, max_length=100)
    last_name: Optional[str] = Field(None, max_length=100)


class UserCreate(UserBase):
    """Schema for creating a user"""
    password: str = Field(..., min_length=8)
    institution_id: Optional[int] = None  # Required for non-superadmin
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "operator@hospital.com",
                "username": "operator1",
                "password": "SecurePass123!",
                "role": "operator",
                "first_name": "Juan",
                "last_name": "Pérez",
                "institution_id": 1
            }
        }


class UserUpdate(BaseModel):
    """Schema for updating a user"""
    email: Optional[EmailStr] = None
    username: Optional[str] = Field(None, min_length=3, max_length=100)
    first_name: Optional[str] = Field(None, max_length=100)
    last_name: Optional[str] = Field(None, max_length=100)
    is_active: Optional[int] = Field(None, ge=0, le=1)
    role: Optional[UserRole] = None


class UserResponse(UserBase):
    """Schema for user response"""
    id: int
    institution_id: Optional[int] = None
    is_active: int
    last_login: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class UserWithInstitution(UserResponse):
    """User response with institution info"""
    institution_name: Optional[str] = None
    
    class Config:
        from_attributes = True


class CurrentUser(BaseModel):
    """Current authenticated user schema"""
    id: int
    email: str
    username: str
    role: UserRole
    institution_id: Optional[int] = None
    institution_name: Optional[str] = None
    full_name: str
    is_active: int
    
    class Config:
        from_attributes = True
