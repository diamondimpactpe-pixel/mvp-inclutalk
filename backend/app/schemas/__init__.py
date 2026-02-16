"""
Schemas package - exports all Pydantic schemas
"""
from app.schemas.auth import Token, TokenPayload, LoginRequest, RefreshTokenRequest, PasswordChange
from app.schemas.institution import (
    InstitutionCreate, InstitutionUpdate, InstitutionResponse, InstitutionWithStats
)
from app.schemas.user import (
    UserCreate, UserUpdate, UserResponse, UserWithInstitution, CurrentUser
)
from app.schemas.session import (
    SessionCreate, SessionUpdate, SessionEnd, SessionResponse, SessionWithDetails, SessionStats
)
from app.schemas.lsp import (
    LSPKeypoint, LSPFrame, LSPSequence, LSPPrediction, LSPVocabulary
)

__all__ = [
    # Auth
    "Token",
    "TokenPayload",
    "LoginRequest",
    "RefreshTokenRequest",
    "PasswordChange",
    # Institution
    "InstitutionCreate",
    "InstitutionUpdate",
    "InstitutionResponse",
    "InstitutionWithStats",
    # User
    "UserCreate",
    "UserUpdate",
    "UserResponse",
    "UserWithInstitution",
    "CurrentUser",
    # Session
    "SessionCreate",
    "SessionUpdate",
    "SessionEnd",
    "SessionResponse",
    "SessionWithDetails",
    "SessionStats",
    # LSP
    "LSPKeypoint",
    "LSPFrame",
    "LSPSequence",
    "LSPPrediction",
    "LSPVocabulary",
]
