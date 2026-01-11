"""
Main FastAPI application for PR Bar Exam API.
Hosted on Railway.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from app.core.config import settings
from app.api import public, quiz, progress, essays, admin

# Configure logging
logging.basicConfig(
    level=logging.INFO if not settings.DEBUG else logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    yield
    logger.info("Shutting down...")


# Initialize FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="""
    AI-powered Puerto Rico Bar Exam preparation API.
    
    ## Features
    - 📝 MCQ quizzes generated from Black Letter Law rules
    - 📖 Essay grading with RAG-based feedback
    - 📊 Progress tracking and weekly analytics
    - 📚 PDF ingestion for study materials
    
    ## Authentication
    - **Public endpoints**: No auth required (`/ping`, `/health`, `/subjects`)
    - **User endpoints**: Supabase JWT token required (`/api/*`)
    - **Admin endpoints**: API key + admin UUID required (`/admin/*`)
    """,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
# Public routes (no auth)
app.include_router(public.router)

# User routes (Supabase auth required)
app.include_router(quiz.router, prefix="/api")
app.include_router(progress.router, prefix="/api")
app.include_router(essays.router, prefix="/api")

# Admin routes (API key + admin UUID required)
app.include_router(admin.router)


@app.get("/")
async def root():
    """Root endpoint with API info."""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "health": "/health"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )