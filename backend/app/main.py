"""
IncluTalk - Main FastAPI Application (CORS FIXED)
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

# Configure CORS - FIXED VERSION
# Allow all origins for development (you can restrict this in production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
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
        "docs": "/api/docs",
        "status": "running"
    }

@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": "1.0.0"
    }

@app.on_event("startup")
async def startup_event():
    """Startup event"""
    log_info("IncluTalk API started")
    log_info(f"Environment: {settings.ENVIRONMENT}")
    log_info(f"ML Demo Mode: {settings.ML_DEMO_MODE}")
    log_info(f"STT Demo Mode: {settings.STT_DEMO_MODE}")
    log_info("CORS enabled for: http://localhost:3000, http://localhost:5173")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=settings.DEBUG)