#!/usr/bin/env python3
"""
Script para generar el proyecto completo IncluTalk MVP
Genera todos los archivos del backend y frontend
"""
import os
import json

# ============================================================================
# BACKEND FILES
# ============================================================================

BACKEND_FILES = {

# ============================================================================
# SERVICES
# ============================================================================

"backend/app/services/auth_service.py": '''"""
Authentication service
"""
from datetime import datetime
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.user import User
from app.schemas.auth import LoginRequest, Token
from app.auth.security import verify_password
from app.auth.jwt import create_access_token, create_refresh_token, decode_token, verify_token_type
from app.utils.logger import log_info


def authenticate_user(db: Session, credentials: LoginRequest) -> User:
    """Authenticate user with email and password"""
    user = db.query(User).filter(User.email == credentials.email).first()
    
    if not user or not verify_password(credentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )
    
    # Update last login
    user.last_login = datetime.utcnow()
    db.commit()
    
    log_info(f"User {user.email} authenticated successfully")
    return user


def create_tokens_for_user(user: User) -> Token:
    """Create access and refresh tokens for user"""
    access_token = create_access_token(data={"sub": user.id})
    refresh_token = create_refresh_token(data={"sub": user.id})
    
    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer"
    )


def refresh_access_token(refresh_token: str, db: Session) -> Token:
    """Refresh access token using refresh token"""
    if not verify_token_type(refresh_token, "refresh"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    
    payload = decode_token(refresh_token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    
    user_id = payload.get("sub")
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive"
        )
    
    return create_tokens_for_user(user)
''',

"backend/app/services/user_service.py": '''"""
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
''',

"backend/app/services/session_service.py": '''"""
Session management service
"""
from datetime import datetime
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.session import Session as SessionModel
from app.models.user import User
from app.schemas.session import SessionCreate, SessionUpdate, SessionEnd
from app.utils.logger import log_info


def create_session(db: Session, operator: User) -> SessionModel:
    """Create a new attention session"""
    session = SessionModel(
        institution_id=operator.institution_id,
        operator_id=operator.id,
        started_at=datetime.utcnow()
    )
    
    db.add(session)
    db.commit()
    db.refresh(session)
    
    log_info(f"Session {session.id} started by operator {operator.username}")
    return session


def get_session(db: Session, session_id: int, current_user: User) -> SessionModel:
    """Get session by ID"""
    session = db.query(SessionModel).filter(SessionModel.id == session_id).first()
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    
    # Verify access
    if current_user.role.value not in ["superadmin"]:
        if session.institution_id != current_user.institution_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    
    return session


def update_session_metrics(db: Session, session_id: int, metrics: SessionUpdate) -> SessionModel:
    """Update session metrics"""
    session = db.query(SessionModel).filter(SessionModel.id == session_id).first()
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    
    for field, value in metrics.dict(exclude_unset=True).items():
        setattr(session, field, value)
    
    db.commit()
    db.refresh(session)
    return session


def end_session(db: Session, session_id: int, end_data: SessionEnd) -> SessionModel:
    """End an attention session"""
    session = db.query(SessionModel).filter(SessionModel.id == session_id).first()
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    
    if session.ended_at:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Session already ended")
    
    session.ended_at = datetime.utcnow()
    session.total_duration_seconds = int((session.ended_at - session.started_at).total_seconds())
    
    if end_data.operator_notes:
        session.operator_notes = end_data.operator_notes
    
    db.commit()
    db.refresh(session)
    
    log_info(f"Session {session.id} ended (duration: {session.duration_minutes} minutes)")
    return session
''',

"backend/app/services/stt_service.py": '''"""
Speech-to-Text service
Mock implementation for MVP - can be replaced with Whisper API
"""
import random
from typing import Optional
from app.utils.logger import log_info, log_warning
from app.config import settings


class STTService:
    """Speech-to-Text service"""
    
    def __init__(self):
        self.demo_mode = settings.STT_DEMO_MODE
        
        if not self.demo_mode:
            try:
                import whisper
                self.model = whisper.load_model(settings.WHISPER_MODEL_SIZE)
                log_info(f"Whisper model loaded: {settings.WHISPER_MODEL_SIZE}")
            except ImportError:
                log_warning("Whisper not available, using demo mode")
                self.demo_mode = True
    
    def transcribe_audio(self, audio_data: bytes) -> dict:
        """
        Transcribe audio to text
        
        Args:
            audio_data: Audio file bytes
            
        Returns:
            Dictionary with text and confidence
        """
        if self.demo_mode:
            return self._transcribe_demo()
        
        # TODO: Implement real Whisper transcription
        # Save audio_data to temp file
        # result = self.model.transcribe(temp_file)
        # return {"text": result["text"], "confidence": 0.95}
        
        return self._transcribe_demo()
    
    def _transcribe_demo(self) -> dict:
        """Demo transcription with sample phrases"""
        sample_phrases = [
            "Necesito renovar mi DNI",
            "Quiero hacer un pago",
            "Tengo una cita programada",
            "Necesito presentar un reclamo",
            "¿Dónde puedo obtener un certificado?",
            "Mi documento está vencido",
            "Necesito ayuda con un trámite",
        ]
        
        text = random.choice(sample_phrases)
        confidence = random.uniform(0.85, 0.98)
        
        return {
            "text": text,
            "confidence": confidence,
            "language": "es"
        }


# Global instance
_stt_service: Optional[STTService] = None


def get_stt_service() -> STTService:
    """Get STT service instance"""
    global _stt_service
    if _stt_service is None:
        _stt_service = STTService()
    return _stt_service
''',

}

# Generar archivos
def generate_files():
    for file_path, content in BACKEND_FILES.items():
        full_path = f"/home/claude/inclutalk/{file_path}"
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, 'w') as f:
            f.write(content)
        print(f"✓ Created: {file_path}")

if __name__ == "__main__":
    generate_files()
    print("\n✅ Services generated successfully!")

