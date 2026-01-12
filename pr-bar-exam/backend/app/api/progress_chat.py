"""
API endpoints for progress tracking.
Chat functionality is handled by Supabase real-time, not database models.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.schemas import schemas
from app.models.models import UserProgress, User, SubjectEnum
from datetime import datetime

progress_router = APIRouter(prefix="/progress", tags=["progress"])


# ==================== PROGRESS ENDPOINTS ====================

@progress_router.get("/user/{user_id}", response_model=schemas.UserProgressOverview)
async def get_user_progress(
    user_id: int,
    db: Session = Depends(get_db)
):
    """
    Get comprehensive progress overview for a user across all subjects.
    """
    # Verify user exists
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Get progress for all subjects
    progress_records = db.query(UserProgress).filter(
        UserProgress.user_id == user_id
    ).all()
    
    subjects_progress = []
    total_attempted = 0
    total_correct = 0
    
    for progress in progress_records:
        accuracy = (progress.correct_answers / progress.total_questions_attempted * 100) if progress.total_questions_attempted > 0 else 0.0
        
        subjects_progress.append(schemas.SubjectProgress(
            subject=progress.subject,
            total_mcqs_attempted=progress.total_questions_attempted,
            total_mcqs_correct=progress.correct_answers,
            accuracy_percentage=round(accuracy, 2),
            total_essays_submitted=progress.total_essays,
            average_essay_score=progress.avg_essay_score,
            last_activity=progress.last_activity or datetime.now()
        ))
        
        total_attempted += progress.total_questions_attempted
        total_correct += progress.correct_answers
    
    overall_accuracy = (total_correct / total_attempted * 100) if total_attempted > 0 else 0.0
    
    return schemas.UserProgressOverview(
        user_id=user_id,
        subjects=subjects_progress,
        overall_accuracy=round(overall_accuracy, 2),
        total_questions_attempted=total_attempted
    )


@progress_router.get("/user/{user_id}/subject/{subject}", response_model=schemas.SubjectProgress)
async def get_subject_progress(
    user_id: int,
    subject: SubjectEnum,
    db: Session = Depends(get_db)
):
    """
    Get detailed progress for a specific subject.
    """
    # Verify user exists
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    progress = db.query(UserProgress).filter(
        UserProgress.user_id == user_id,
        UserProgress.subject == subject
    ).first()
    
    if not progress:
        # Return empty progress if no records exist
        return schemas.SubjectProgress(
            subject=subject,
            total_mcqs_attempted=0,
            total_mcqs_correct=0,
            accuracy_percentage=0.0,
            total_essays_submitted=0,
            average_essay_score=None,
            last_activity=datetime.now()
        )
    
    accuracy = (progress.correct_answers / progress.total_questions_attempted * 100) if progress.total_questions_attempted > 0 else 0.0
    
    return schemas.SubjectProgress(
        subject=progress.subject,
        total_mcqs_attempted=progress.total_questions_attempted,
        total_mcqs_correct=progress.correct_answers,
        accuracy_percentage=round(accuracy, 2),
        total_essays_submitted=progress.total_essays,
        average_essay_score=progress.avg_essay_score,
        last_activity=progress.last_activity or datetime.now()
    )