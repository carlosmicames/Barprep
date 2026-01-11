"""
Pydantic schemas for request/response validation.
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from app.models.models import SubjectEnum


# User Schemas
class UserBase(BaseModel):
    email: EmailStr
    username: str
    full_name: Optional[str] = None


class UserCreate(UserBase):
    pass


class User(UserBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


# Study Material Schemas
class StudyMaterialUpload(BaseModel):
    subject: SubjectEnum
    title: str
    is_official: bool = False


class StudyMaterial(BaseModel):
    id: int
    subject: SubjectEnum
    title: str
    file_type: str
    is_official: bool
    uploaded_at: datetime
    processed: bool
    
    class Config:
        from_attributes = True


# MCQ Schemas
class MCQOption(BaseModel):
    label: str
    text: str


class MCQBase(BaseModel):
    subject: SubjectEnum
    question_text: str
    option_a: str
    option_b: str
    option_c: str
    option_d: str
    correct_answer: str
    explanation: Optional[str] = None
    difficulty: str = "medium"


class MCQCreate(MCQBase):
    pass


class MCQuestion(MCQBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class MCQWithoutAnswer(BaseModel):
    """MCQ without revealing the correct answer (for students)."""
    id: int
    subject: SubjectEnum
    question_text: str
    options: List[MCQOption]
    difficulty: str
    
    class Config:
        from_attributes = True


class MCQResponseCreate(BaseModel):
    question_id: int
    selected_answer: str
    time_spent_seconds: Optional[int] = None


class MCQResponseResult(BaseModel):
    is_correct: bool
    correct_answer: str
    explanation: Optional[str]
    selected_answer: str


class MCQGenerateRequest(BaseModel):
    subject: SubjectEnum
    num_questions: int = Field(default=10, ge=1, le=50)
    difficulty: Optional[str] = "medium"


# Essay Schemas
class EssaySubmit(BaseModel):
    subject: SubjectEnum
    prompt: str
    content: str


class EssayGradeResponse(BaseModel):
    overall_score: float
    legal_analysis_score: Optional[float]
    writing_quality_score: Optional[float]
    citation_accuracy_score: Optional[float]
    feedback: str
    point_breakdown: Dict[str, Any]
    citations: List[Dict[str, str]]


class Essay(BaseModel):
    id: int
    user_id: int
    subject: SubjectEnum
    prompt: str
    content: str
    submitted_at: datetime
    grade: Optional[EssayGradeResponse] = None
    
    class Config:
        from_attributes = True


# Progress Schemas
class SubjectProgress(BaseModel):
    subject: SubjectEnum
    total_mcqs_attempted: int
    total_mcqs_correct: int
    accuracy_percentage: float
    total_essays_submitted: int
    average_essay_score: Optional[float]
    last_activity: datetime


class UserProgressOverview(BaseModel):
    user_id: int
    subjects: List[SubjectProgress]
    overall_accuracy: float
    total_questions_attempted: int


# Chat Schemas
class ChatMessageCreate(BaseModel):
    room_id: int
    message: str


class ChatMessage(BaseModel):
    id: int
    room_id: int
    user_id: int
    message: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class ChatRoom(BaseModel):
    id: int
    subject: SubjectEnum
    name: str
    description: Optional[str]
    
    class Config:
        from_attributes = True


# RAG Schemas
class RAGQuery(BaseModel):
    query: str
    subject: SubjectEnum
    top_k: int = Field(default=5, ge=1, le=20)


class RAGResult(BaseModel):
    text: str
    source: str
    page_number: Optional[int]
    similarity_score: float


# Admin & BLL Rule Schemas (ADDED - These were missing!)
class BLLRule(BaseModel):
    """Business Logic Layer rule representation."""
    id: Optional[int] = None
    rule_number: str
    title: str
    content: str
    subject: SubjectEnum
    article_number: Optional[str] = None
    section: Optional[str] = None
    created_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class BLLRuleIngest(BaseModel):
    """Response model for BLL rule ingestion."""
    success: bool
    rules_ingested: int
    message: str
    rules: Optional[List[BLLRule]] = None


class UserInfo(BaseModel):
    """User information for admin views."""
    id: int
    email: str
    username: str
    full_name: Optional[str] = None
    is_admin: bool
    created_at: datetime
    total_questions_attempted: int = 0
    total_essays_submitted: int = 0
    
    class Config:
        from_attributes = True


class AdminStats(BaseModel):
    """Admin dashboard statistics."""
    total_users: int
    total_questions: int
    total_essays: int
    total_materials: int
    total_bll_rules: int = 0
    active_users_today: int = 0
    active_users_week: int = 0
    questions_by_subject: Dict[str, int] = {}
    essays_by_subject: Dict[str, int] = {}