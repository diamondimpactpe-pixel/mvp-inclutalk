"""
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
