"""
Authentication and authorization middleware (FIXED VERSION)
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.database import get_db
from app.auth.jwt import decode_token
from app.models.user import User, UserRole
from typing import Optional

security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Get current authenticated user from JWT token
    
    Args:
        credentials: HTTP authorization credentials
        db: Database session
        
    Returns:
        Current user object
        
    Raises:
        HTTPException: If token is invalid or user not found
    """
    print(f"\n{'='*60}")
    print(f"🔐 MIDDLEWARE: Validando token...")
    print(f"Token recibido (primeros 50 chars): {credentials.credentials[:50]}...")
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    token = credentials.credentials
    
    # Decode token
    print(f"🔓 Decodificando token...")
    payload = decode_token(token)
    
    if payload is None:
        print(f"❌ ERROR: Token inválido o expirado")
        print(f"{'='*60}\n")
        raise credentials_exception
    
    print(f"✅ Token decodificado correctamente")
    print(f"Payload: {payload}")
    
    # Get user ID from token
    user_id: int = payload.get("sub")
    if user_id is None:
        print(f"❌ ERROR: No hay user_id en el payload")
        print(f"{'='*60}\n")
        raise credentials_exception
    
    print(f"👤 Buscando usuario ID: {user_id}")
    
    # Get user from database
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        print(f"❌ ERROR: Usuario {user_id} no encontrado en la base de datos")
        print(f"{'='*60}\n")
        raise credentials_exception
    
    print(f"✅ Usuario encontrado: {user.email}")
    
    # Check if user is active
    if not user.is_active:
        print(f"❌ ERROR: Usuario {user.email} está inactivo")
        print(f"{'='*60}\n")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )
    
    print(f"✅ Usuario activo y autenticado")
    print(f"{'='*60}\n")
    
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Get current active user
    
    Args:
        current_user: Current user from get_current_user
        
    Returns:
        Current active user
        
    Raises:
        HTTPException: If user is inactive
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )
    return current_user


async def require_role(
    required_roles: list[UserRole],
    current_user: User = Depends(get_current_active_user)
) -> User:
    """
    Require user to have specific role(s)
    
    Args:
        required_roles: List of required roles
        current_user: Current active user
        
    Returns:
        Current user if authorized
        
    Raises:
        HTTPException: If user doesn't have required role
    """
    if current_user.role not in required_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Insufficient permissions. Required roles: {[r.value for r in required_roles]}"
        )
    return current_user


def require_admin(current_user: User = Depends(get_current_active_user)) -> User:
    """
    Require user to be an admin or superadmin
    
    Args:
        current_user: Current active user
        
    Returns:
        Current user if authorized
    """
    if current_user.role not in [UserRole.ADMIN, UserRole.SUPERADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    return current_user


def require_superadmin(current_user: User = Depends(get_current_active_user)) -> User:
    """
    Require user to be a superadmin
    
    Args:
        current_user: Current active user
        
    Returns:
        Current user if authorized
    """
    if current_user.role != UserRole.SUPERADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Superadmin privileges required"
        )
    return current_user


def verify_institution_access(
    user: User,
    institution_id: int,
    allow_superadmin: bool = True
) -> bool:
    """
    Verify if user has access to an institution
    
    Args:
        user: User to verify
        institution_id: Institution ID to check access for
        allow_superadmin: Allow superadmin to access any institution
        
    Returns:
        True if user has access, False otherwise
    """
    # Superadmin has access to all institutions
    if allow_superadmin and user.role == UserRole.SUPERADMIN:
        return True
    
    # User must belong to the institution
    return user.institution_id == institution_id