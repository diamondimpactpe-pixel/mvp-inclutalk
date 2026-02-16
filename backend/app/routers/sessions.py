"""Sessions router"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.schemas.session import SessionCreate, SessionResponse, SessionEnd, SessionUpdate
from app.services.session_service import create_session, get_session, end_session, update_session_metrics
from app.auth.middleware import get_current_active_user
from app.models.user import User

router = APIRouter(prefix="/sessions", tags=["Sessions"])

@router.post("/start", response_model=SessionResponse)
def start_session(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Start a new attention session"""
    session = create_session(db, current_user)
    return session

@router.get("/{session_id}", response_model=SessionResponse)
def get_session_info(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get session information"""
    return get_session(db, session_id, current_user)

@router.patch("/{session_id}/metrics")
def update_metrics(
    session_id: int,
    metrics: SessionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update session metrics"""
    return update_session_metrics(db, session_id, metrics)

@router.post("/{session_id}/end", response_model=SessionResponse)
def end_session_endpoint(
    session_id: int,
    end_data: SessionEnd,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """End an attention session"""
    return end_session(db, session_id, end_data)
