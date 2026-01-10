"""
SQLAlchemy database models for PR Bar Exam platform.
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Float, Boolean, JSON, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import enum
from app.core.database import Base
from pgvector.sqlalchemy import Vector


class SubjectEnum(str, enum.Enum):
    """Enum for the 13 PR bar exam subjects."""
    FAMILIA = "familia"  # Family Law
    SUCESIONES = "sucesiones"  # Succession
    REALES = "reales"  # Property Rights
    HIPOTECA = "hipoteca"  # Mortgage
    OBLIGACIONES = "obligaciones"  # Obligations & Contracts
    ETICA = "etica"  # Ethics
    CONSTITUCIONAL = "constitucional"  # Constitutional Law
    ADMINISTRATIVO = "administrativo"  # Administrative Law
    DANOS = "danos"  # Damages
    PENAL = "penal"  # Criminal Law
    PROC_PENAL = "proc_penal"  # Criminal Procedure
    EVIDENCIA = "evidencia"  # Evidence
    PROC_CIVIL = "proc_civil"  # Civil Procedure


class User(Base):
    """User model for students."""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    mcq_responses = relationship("MCQResponse", back_populates="user")
    essays = relationship("Essay", back_populates="user")
    progress = relationship("UserProgress", back_populates="user")
    uploads = relationship("StudyMaterial", back_populates="user")


class StudyMaterial(Base):
    """Study materials uploaded by users or admins."""
    __tablename__ = "study_materials"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # Null for official materials
    subject = Column(Enum(SubjectEnum), nullable=False)
    title = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    file_type = Column(String, nullable=False)  # pdf, docx
    is_official = Column(Boolean, default=False)  # Official PR codes vs user uploads
    uploaded_at = Column(DateTime, server_default=func.now())
    processed = Column(Boolean, default=False)  # Whether embeddings are created
    
    # Relationships
    user = relationship("User", back_populates="uploads")
    chunks = relationship("DocumentChunk", back_populates="material")


class DocumentChunk(Base):
    """Chunked documents with embeddings for RAG."""
    __tablename__ = "document_chunks"
    
    id = Column(Integer, primary_key=True, index=True)
    material_id = Column(Integer, ForeignKey("study_materials.id"), nullable=False)
    chunk_text = Column(Text, nullable=False)
    chunk_index = Column(Integer, nullable=False)
    page_number = Column(Integer)
    embedding = Column(Vector(1536))  # OpenAI embedding dimension
    metadata = Column(JSON)  # Store additional context
    created_at = Column(DateTime, server_default=func.now())
    
    # Relationships
    material = relationship("StudyMaterial", back_populates="chunks")


class MCQuestion(Base):
    """Multiple choice questions."""
    __tablename__ = "mcq_questions"
    
    id = Column(Integer, primary_key=True, index=True)
    subject = Column(Enum(SubjectEnum), nullable=False)
    question_text = Column(Text, nullable=False)
    option_a = Column(Text, nullable=False)
    option_b = Column(Text, nullable=False)
    option_c = Column(Text, nullable=False)
    option_d = Column(Text, nullable=False)
    correct_answer = Column(String(1), nullable=False)  # A, B, C, or D
    explanation = Column(Text)
    difficulty = Column(String, default="medium")  # easy, medium, hard
    source_material_id = Column(Integer, ForeignKey("study_materials.id"))
    created_at = Column(DateTime, server_default=func.now())
    
    # Relationships
    responses = relationship("MCQResponse", back_populates="question")


class MCQResponse(Base):
    """User responses to MCQs."""
    __tablename__ = "mcq_responses"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    question_id = Column(Integer, ForeignKey("mcq_questions.id"), nullable=False)
    selected_answer = Column(String(1), nullable=False)  # A, B, C, or D
    is_correct = Column(Boolean, nullable=False)
    time_spent_seconds = Column(Integer)
    answered_at = Column(DateTime, server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="mcq_responses")
    question = relationship("MCQuestion", back_populates="responses")


class Essay(Base):
    """Essay submissions by users."""
    __tablename__ = "essays"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    subject = Column(Enum(SubjectEnum), nullable=False)
    prompt = Column(Text, nullable=False)
    content = Column(Text, nullable=False)
    submitted_at = Column(DateTime, server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="essays")
    grade = relationship("EssayGrade", back_populates="essay", uselist=False)


class EssayGrade(Base):
    """AI-generated grades for essays."""
    __tablename__ = "essay_grades"
    
    id = Column(Integer, primary_key=True, index=True)
    essay_id = Column(Integer, ForeignKey("essays.id"), nullable=False, unique=True)
    overall_score = Column(Float, nullable=False)  # 0-100
    legal_analysis_score = Column(Float)
    writing_quality_score = Column(Float)
    citation_accuracy_score = Column(Float)
    feedback = Column(Text, nullable=False)
    point_breakdown = Column(JSON)  # Detailed scoring breakdown
    citations = Column(JSON)  # Referenced legal sources
    graded_at = Column(DateTime, server_default=func.now())
    
    # Relationships
    essay = relationship("Essay", back_populates="grade")


class UserProgress(Base):
    """Track user progress by subject."""
    __tablename__ = "user_progress"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    subject = Column(Enum(SubjectEnum), nullable=False)
    total_mcqs_attempted = Column(Integer, default=0)
    total_mcqs_correct = Column(Integer, default=0)
    total_essays_submitted = Column(Integer, default=0)
    average_essay_score = Column(Float)
    last_activity = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="progress")


class ChatRoom(Base):
    """Chat rooms for different subjects."""
    __tablename__ = "chat_rooms"
    
    id = Column(Integer, primary_key=True, index=True)
    subject = Column(Enum(SubjectEnum), nullable=False, unique=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    created_at = Column(DateTime, server_default=func.now())
    
    # Relationships
    messages = relationship("ChatMessage", back_populates="room")


class ChatMessage(Base):
    """Messages in chat rooms."""
    __tablename__ = "chat_messages"
    
    id = Column(Integer, primary_key=True, index=True)
    room_id = Column(Integer, ForeignKey("chat_rooms.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    message = Column(Text, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    
    # Relationships
    room = relationship("ChatRoom", back_populates="messages")
