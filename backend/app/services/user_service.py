"""
User management service
"""
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import List, Optional
from app.models.user import User, UserRole
from app.models.institution import Institution
from app.schemas.user import UserCreate, UserUpdate
from app.auth.security import get_password_hash, validate_password_strength
from app.utils.logger import log_info, log_error


def create_user(db: Session, user_data: UserCreate, creator: User) -> User:
    """Create a new user"""
    # Validate password strength
    is_valid, error_msg = validate_password_strength(user_data.password)
    if not is_valid:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error_msg)
    
    # Check if email already exists
    existing = db.query(User).filter(User.email == user_data.email).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    
    # Check username
    existing = db.query(User).filter(User.username == user_data.username).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already taken")
    
    # Verify institution access
    if user_data.role != UserRole.SUPERADMIN:
        if not user_data.institution_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Institution ID required")
        
        # Verify institution exists
        institution = db.query(Institution).filter(Institution.id == user_data.institution_id).first()
        if not institution:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Institution not found")
        
        # Only superadmin or same institution admin can create users
        if creator.role != UserRole.SUPERADMIN:
            if creator.institution_id != user_data.institution_id:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cannot create user for different institution")
    
    # Create user
    user = User(
        email=user_data.email,
        username=user_data.username,
        password_hash=get_password_hash(user_data.password),
        role=user_data.role,
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        institution_id=user_data.institution_id
    )
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    log_info(f"User created: {user.email} (role: {user.role})")
    return user


def get_users(db: Session, current_user: User, skip: int = 0, limit: int = 100) -> List[User]:
    """Get list of users"""
    query = db.query(User)
    
    # Filter by institution for non-superadmin
    if current_user.role != UserRole.SUPERADMIN:
        query = query.filter(User.institution_id == current_user.institution_id)
    
    return query.offset(skip).limit(limit).all()


def update_user(db: Session, user_id: int, update_data: UserUpdate, current_user: User) -> User:
    """Update user"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    # Check permissions
    if current_user.role != UserRole.SUPERADMIN:
        if user.institution_id != current_user.institution_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    
    # Update fields
    for field, value in update_data.dict(exclude_unset=True).items():
        setattr(user, field, value)
    
    db.commit()
    db.refresh(user)
    
    log_info(f"User updated: {user.email}")
    return user
