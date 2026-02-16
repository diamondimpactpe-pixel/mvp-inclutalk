#!/bin/bash

# Script para generar TODO el MVP de IncluTalk

echo "🚀 Generando MVP completo de IncluTalk..."

# ============================================================================
# BACKEND - ROUTERS
# ============================================================================

cat > backend/app/routers/auth.py << 'EOF'
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
EOF

cat > backend/app/routers/lsp.py << 'EOF'
"""LSP (Lengua de Señas) recognition router"""
from fastapi import APIRouter, Depends, HTTPException
from app.schemas.lsp import LSPSequence, LSPPrediction, LSPVocabulary
from app.ml.predict import predict_lsp_sequence, get_available_vocabulary
from app.utils.logger import log_info, log_error

router = APIRouter(prefix="/lsp", tags=["LSP Recognition"])

@router.post("/predict", response_model=LSPPrediction)
def predict_sign(sequence: LSPSequence):
    """
    Predict sign language word from keypoint sequence
    """
    try:
        prediction = predict_lsp_sequence(sequence)
        return prediction
    except Exception as e:
        log_error(f"Error in LSP prediction: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")

@router.get("/vocabulary", response_model=LSPVocabulary)
def get_vocabulary():
    """Get available LSP vocabulary"""
    words = get_available_vocabulary()
    return LSPVocabulary(words=words, total_count=len(words))
EOF

cat > backend/app/routers/sessions.py << 'EOF'
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
EOF

echo "✅ Routers creados"

# ============================================================================
# BACKEND - MAIN.PY
# ============================================================================

cat > backend/app/main.py << 'EOF'
"""
IncluTalk - Main FastAPI Application
B2B SaaS for inclusive attention with LSP (Peruvian Sign Language)
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from app.config import settings
from app.utils.rate_limiter import limiter
from app.utils.logger import log_info
from app.routers import auth, lsp, sessions

# Create FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    description="Inclusive attention platform with LSP recognition",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# Add rate limiter
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix=settings.API_V1_PREFIX)
app.include_router(lsp.router, prefix=settings.API_V1_PREFIX)
app.include_router(sessions.router, prefix=settings.API_V1_PREFIX)

@app.get("/")
def root():
    """Root endpoint"""
    return {
        "message": "IncluTalk API",
        "version": "1.0.0",
        "docs": "/api/docs"
    }

@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

@app.on_event("startup")
async def startup_event():
    """Startup event"""
    log_info("IncluTalk API started")
    log_info(f"Environment: {settings.ENVIRONMENT}")
    log_info(f"ML Demo Mode: {settings.ML_DEMO_MODE}")
    log_info(f"STT Demo Mode: {settings.STT_DEMO_MODE}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=settings.DEBUG)
EOF

echo "✅ Main.py creado"

# ============================================================================
# BACKEND - DOCKER
# ============================================================================

cat > backend/Dockerfile << 'EOF'
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Expose port
EXPOSE 8000

# Run application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
EOF

cat > backend/docker-compose.yml << 'EOF'
version: '3.8'

services:
  db:
    image: postgres:15-alpine
    environment:
      POSTGRES_USER: inclutalk_user
      POSTGRES_PASSWORD: inclutalk_pass
      POSTGRES_DB: inclutalk_db
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U inclutalk_user"]
      interval: 10s
      timeout: 5s
      retries: 5

  backend:
    build: .
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql://inclutalk_user:inclutalk_pass@db:5432/inclutalk_db
    depends_on:
      db:
        condition: service_healthy
    volumes:
      - ./app:/app/app
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

volumes:
  postgres_data:
EOF

echo "✅ Docker files creados"

# ============================================================================
# BACKEND - ALEMBIC
# ============================================================================

cat > backend/alembic.ini << 'EOF'
[alembic]
script_location = alembic
prepend_sys_path = .
version_path_separator = os
sqlalchemy.url = postgresql://inclutalk_user:inclutalk_pass@localhost:5432/inclutalk_db

[loggers]
keys = root,sqlalchemy,alembic

[handlers]
keys = console

[formatters]
keys = generic

[logger_root]
level = WARN
handlers = console

[logger_sqlalchemy]
level = WARN
handlers =
qualname = sqlalchemy.engine

[logger_alembic]
level = INFO
handlers =
qualname = alembic

[handler_console]
class = StreamHandler
args = (sys.stderr,)
level = NOTSET
formatter = generic

[formatter_generic]
format = %(levelname)-5.5s [%(name)s] %(message)s
datefmt = %H:%M:%S
EOF

mkdir -p backend/alembic/versions

cat > backend/alembic/env.py << 'EOF'
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
import sys
import os

sys.path.insert(0, os.path.realpath(os.path.join(os.path.dirname(__file__), '..')))

from app.database import Base
from app.models import *

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
EOF

cat > backend/alembic/script.py.mako << 'EOF'
"""${message}

Revision ID: ${up_revision}
Revises: ${down_revision | comma,n}
Create Date: ${create_date}

"""
from alembic import op
import sqlalchemy as sa
${imports if imports else ""}

revision = ${repr(up_revision)}
down_revision = ${repr(down_revision)}
branch_labels = ${repr(branch_labels)}
depends_on = ${repr(depends_on)}


def upgrade() -> None:
    ${upgrades if upgrades else "pass"}


def downgrade() -> None:
    ${downgrades if downgrades else "pass"}
EOF

echo "✅ Alembic configurado"

echo ""
echo "=========================================="
echo "✅ BACKEND COMPLETO GENERADO"
echo "=========================================="
echo ""
echo "Archivos generados:"
echo "  - Routers (auth, lsp, sessions)"
echo "  - Main FastAPI app"
echo "  - Docker & docker-compose"
echo "  - Alembic configuration"
echo ""

