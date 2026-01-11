"""
Database models for the PR Bar Exam application.
"""
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, JSON, Float, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
from app.core.database import Base
import enum

# Import pgvector for embeddings
try:
    from pgvector.sqlalchemy import Vector
except ImportError:
    # Fallback if pgvector not available
    Vector = None


# Enums
class SubjectEnum(str, enum.Enum):
    """Bar exam subjects."""
    FAMILIA = "familia"
    SUCESIONES = "sucesiones"
    REALES = "reales"
    HIPOTECA = "hipoteca"
    OBLIGACIONES = "obligaciones"
    ETICA = "etica"
    CONSTITUCIONAL = "constitucional"
    ADMINISTRATIVO = "administrativo"
    DANOS = "danos"
    PENAL = "penal"
    PROC_PENAL = "proc_penal"
    EVIDENCIA = "evidencia"
    PROC_CIVIL = "proc_civil"


class DifficultyEnum(str, enum.Enum):
    """Question difficulty levels."""
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


# Models
class User(Base):
    """User account model."""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    full_name = Column(String(255))
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    materials = relationship("StudyMaterial", back_populates="user")
    quiz_attempts = relationship("QuizAttempt", back_populates="user")
    essay_submissions = relationship("EssaySubmission", back_populates="user")


class StudyMaterial(Base):
    """Study material/document model."""
    __tablename__ = "study_materials"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(500), nullable=False)
    subject = Column(SQLEnum(SubjectEnum), nullable=False, index=True)
    file_path = Column(String(1000))
    file_size = Column(Integer)
    is_official = Column(Boolean, default=False)
    is_processed = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="materials")
    chunks = relationship("DocumentChunk", back_populates="material", cascade="all, delete-orphan")


class DocumentChunk(Base):
    """Document chunk with embeddings for RAG."""
    __tablename__ = "document_chunks"
    
    id = Column(Integer, primary_key=True, index=True)
    material_id = Column(Integer, ForeignKey("study_materials.id"), nullable=False)
    content = Column(Text, nullable=False)
    chunk_index = Column(Integer, nullable=False)
    
    # FIXED: Renamed from 'metadata' to 'doc_metadata' to avoid SQLAlchemy conflict
    doc_metadata = Column(JSON, default={})
    
    # Embedding vector for semantic search
    embedding = Column(Vector(1536) if Vector else JSON)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    material = relationship("StudyMaterial", back_populates="chunks")


class Question(Base):
    """Multiple choice question model."""
    __tablename__ = "questions"
    
    id = Column(Integer, primary_key=True, index=True)
    subject = Column(SQLEnum(SubjectEnum), nullable=False, index=True)
    question_text = Column(Text, nullable=False)
    option_a = Column(Text, nullable=False)
    option_b = Column(Text, nullable=False)
    option_c = Column(Text, nullable=False)
    option_d = Column(Text, nullable=False)
    correct_answer = Column(String(1), nullable=False)
    explanation = Column(Text)
    difficulty = Column(SQLEnum(DifficultyEnum), default=DifficultyEnum.MEDIUM)
    source_material_id = Column(Integer, ForeignKey("study_materials.id"))
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    attempts = relationship("QuestionAttempt", back_populates="question")


class QuizAttempt(Base):
    """Quiz session model."""
    __tablename__ = "quiz_attempts"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    subject = Column(SQLEnum(SubjectEnum), nullable=False)
    total_questions = Column(Integer, nullable=False)
    correct_answers = Column(Integer, default=0)
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True))
    
    # Relationships
    user = relationship("User", back_populates="quiz_attempts")
    question_attempts = relationship("QuestionAttempt", back_populates="quiz_attempt", cascade="all, delete-orphan")


class QuestionAttempt(Base):
    """Individual question attempt within a quiz."""
    __tablename__ = "question_attempts"
    
    id = Column(Integer, primary_key=True, index=True)
    quiz_attempt_id = Column(Integer, ForeignKey("quiz_attempts.id"), nullable=False)
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False)
    user_answer = Column(String(1))
    is_correct = Column(Boolean)
    time_spent = Column(Integer)  # seconds
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    quiz_attempt = relationship("QuizAttempt", back_populates="question_attempts")
    question = relationship("Question", back_populates="attempts")


class EssayPrompt(Base):
    """Essay question prompt model."""
    __tablename__ = "essay_prompts"
    
    id = Column(Integer, primary_key=True, index=True)
    subject = Column(SQLEnum(SubjectEnum), nullable=False, index=True)
    prompt_text = Column(Text, nullable=False)
    grading_rubric = Column(JSON)
    max_score = Column(Integer, default=100)
    time_limit = Column(Integer)  # minutes
    is_official = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    submissions = relationship("EssaySubmission", back_populates="prompt")


class EssaySubmission(Base):
    """Essay submission and grading model."""
    __tablename__ = "essay_submissions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    prompt_id = Column(Integer, ForeignKey("essay_prompts.id"), nullable=False)
    essay_text = Column(Text, nullable=False)
    score = Column(Float)
    feedback = Column(JSON)
    word_count = Column(Integer)
    time_spent = Column(Integer)  # seconds
    submitted_at = Column(DateTime(timezone=True), server_default=func.now())
    graded_at = Column(DateTime(timezone=True))
    
    # Relationships
    user = relationship("User", back_populates="essay_submissions")
    prompt = relationship("EssayPrompt", back_populates="submissions")


class UserProgress(Base):
    """User progress tracking per subject."""
    __tablename__ = "user_progress"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    subject = Column(SQLEnum(SubjectEnum), nullable=False, index=True)
    total_questions_attempted = Column(Integer, default=0)
    correct_answers = Column(Integer, default=0)
    total_essays = Column(Integer, default=0)
    avg_essay_score = Column(Float)
    last_activity = Column(DateTime(timezone=True))
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())