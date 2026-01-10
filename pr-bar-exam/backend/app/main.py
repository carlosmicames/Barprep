"""
Main FastAPI application for PR Bar Exam Prep Platform.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import Base, engine
from app.api import users, mcq, essays, materials, progress_chat

# Create database tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI-powered Puerto Rico Bar Exam preparation platform",
    docs_url="/docs",
    redoc_url="/redoc"
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
app.include_router(users.router)
app.include_router(mcq.router)
app.include_router(essays.router)
app.include_router(materials.router)
app.include_router(progress_chat.progress_router)
app.include_router(progress_chat.chat_router)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "PR Bar Exam Prep API",
        "version": settings.APP_VERSION,
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "environment": settings.ENVIRONMENT
    }


@app.get("/subjects")
async def get_subjects():
    """Get list of all available subjects."""
    from app.models.models import SubjectEnum
    return {
        "subjects": [
            {
                "code": subject.value,
                "name": subject.value.replace("_", " ").title()
            }
            for subject in SubjectEnum
        ]
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )
