"""Authentication router"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.auth import LoginRequest, Token, RefreshTokenRequest
from app.schemas.user import CurrentUser
from app.services.auth_service import authenticate_user, create_tokens_for_user, refresh_access_token
from app.auth.middleware import get_current_active_user
from app.models.user import User

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/login", response_model=Token)
def login(credentials: LoginRequest, db: Session = Depends(get_db)):
    """Login endpoint"""
    user = authenticate_user(db, credentials)
    return create_tokens_for_user(user)

@router.post("/refresh", response_model=Token)
def refresh(request: RefreshTokenRequest, db: Session = Depends(get_db)):
    """Refresh access token"""
    return refresh_access_token(request.refresh_token, db)

@router.post("/logout")
def logout():
    """Logout endpoint (client-side token removal)"""
    return {"message": "Logged out successfully"}

@router.get("/me", response_model=CurrentUser)
def get_me(current_user: User = Depends(get_current_active_user)):
    """Get current user info"""
    return CurrentUser(
        id=current_user.id,
        email=current_user.email,
        username=current_user.username,
        role=current_user.role,
        institution_id=current_user.institution_id,
        institution_name=current_user.institution.name if current_user.institution else None,
        full_name=current_user.full_name,
        is_active=current_user.is_active
    )
