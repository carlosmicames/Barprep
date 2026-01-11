"""
Pydantic schemas package initialization.
Re-exports all schemas and enums for convenient imports.
"""

# Import and re-export everything from schemas.py
from app.schemas.schemas import (
    # Enums
    SubjectEnum,
    
    # User schemas
    UserBase,
    UserCreate,
    User,
    
    # Study Material schemas
    StudyMaterialUpload,
    StudyMaterial,
    
    # MCQ schemas
    MCQOption,
    MCQBase,
    MCQCreate,
    MCQuestion,
    MCQWithoutAnswer,
    MCQResponseCreate,
    MCQResponseResult,
    MCQGenerateRequest,
    
    # Essay schemas
    EssaySubmit,
    EssayGradeResponse,
    Essay,
    
    # Progress schemas
    SubjectProgress,
    UserProgressOverview,
    
    # Chat schemas
    ChatMessageCreate,
    ChatMessage,
    ChatRoom,
    
    # RAG schemas
    RAGQuery,
    RAGResult,
)

# Also import DifficultyEnum from models if needed
from app.models.models import DifficultyEnum

__all__ = [
    # Enums
    "SubjectEnum",
    "DifficultyEnum",
    
    # User schemas
    "UserBase",
    "UserCreate",
    "User",
    
    # Study Material schemas
    "StudyMaterialUpload",
    "StudyMaterial",
    
    # MCQ schemas
    "MCQOption",
    "MCQBase",
    "MCQCreate",
    "MCQuestion",
    "MCQWithoutAnswer",
    "MCQResponseCreate",
    "MCQResponseResult",
    "MCQGenerateRequest",
    
    # Essay schemas
    "EssaySubmit",
    "EssayGradeResponse",
    "Essay",
    
    # Progress schemas
    "SubjectProgress",
    "UserProgressOverview",
    
    # Chat schemas
    "ChatMessageCreate",
    "ChatMessage",
    "ChatRoom",
    
    # RAG schemas
    "RAGQuery",
    "RAGResult",
]