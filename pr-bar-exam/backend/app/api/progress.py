"""
Progress tracking API endpoints.
Re-exports progress_router from progress_chat module.
"""
from app.api.progress_chat import progress_router as router

__all__ = ["router"]