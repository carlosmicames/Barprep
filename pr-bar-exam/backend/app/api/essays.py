"""
API endpoints for essay submission and grading.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.schemas import schemas
from app.models.models import Essay, EssayGrade, User, UserProgress
from app.services.rag_service import rag_service
from datetime import datetime

router = APIRouter(prefix="/essays", tags=["essays"])


@router.post("/submit/{user_id}", response_model=schemas.Essay)
async def submit_essay(
    user_id: int,
    essay_data: schemas.EssaySubmit,
    db: Session = Depends(get_db)
):
    """
    Submit an essay for AI grading.
    """
    # Verify user exists
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    try:
        # Create essay record
        essay = Essay(
            user_id=user_id,
            subject=essay_data.subject,
            prompt=essay_data.prompt,
            content=essay_data.content
        )
        db.add(essay)
        db.flush()
        
        # Grade the essay using RAG
        grade_data = rag_service.grade_essay(
            db=db,
            essay_content=essay_data.content,
            subject=essay_data.subject,
            prompt=essay_data.prompt
        )
        
        # Create grade record
        essay_grade = EssayGrade(
            essay_id=essay.id,
            overall_score=grade_data["overall_score"],
            legal_analysis_score=grade_data.get("legal_analysis_score"),
            writing_quality_score=grade_data.get("writing_quality_score"),
            citation_accuracy_score=grade_data.get("citation_accuracy_score"),
            feedback=grade_data["feedback"],
            point_breakdown=grade_data.get("point_breakdown", {}),
            citations=grade_data.get("citations", [])
        )
        db.add(essay_grade)
        
        # Update user progress
        progress = db.query(UserProgress).filter(
            UserProgress.user_id == user_id,
            UserProgress.subject == essay_data.subject
        ).first()
        
        if progress:
            progress.total_essays_submitted += 1
            # Calculate new average
            if progress.average_essay_score:
                total_score = progress.average_essay_score * (progress.total_essays_submitted - 1)
                progress.average_essay_score = (total_score + grade_data["overall_score"]) / progress.total_essays_submitted
            else:
                progress.average_essay_score = grade_data["overall_score"]
            progress.last_activity = datetime.now()
        else:
            progress = UserProgress(
                user_id=user_id,
                subject=essay_data.subject,
                total_mcqs_attempted=0,
                total_mcqs_correct=0,
                total_essays_submitted=1,
                average_essay_score=grade_data["overall_score"]
            )
            db.add(progress)
        
        db.commit()
        db.refresh(essay)
        
        # Format response
        return schemas.Essay(
            id=essay.id,
            user_id=essay.user_id,
            subject=essay.subject,
            prompt=essay.prompt,
            content=essay.content,
            submitted_at=essay.submitted_at,
            grade=schemas.EssayGradeResponse(
                overall_score=essay_grade.overall_score,
                legal_analysis_score=essay_grade.legal_analysis_score,
                writing_quality_score=essay_grade.writing_quality_score,
                citation_accuracy_score=essay_grade.citation_accuracy_score,
                feedback=essay_grade.feedback,
                point_breakdown=essay_grade.point_breakdown,
                citations=essay_grade.citations
            )
        )
    
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to grade essay: {str(e)}"
        )


@router.get("/user/{user_id}", response_model=List[schemas.Essay])
async def get_user_essays(
    user_id: int,
    subject: str = None,
    db: Session = Depends(get_db)
):
    """
    Get all essays submitted by a user.
    """
    query = db.query(Essay).filter(Essay.user_id == user_id)
    
    if subject:
        query = query.filter(Essay.subject == subject)
    
    essays = query.order_by(Essay.submitted_at.desc()).all()
    
    result = []
    for essay in essays:
        grade = db.query(EssayGrade).filter(EssayGrade.essay_id == essay.id).first()
        
        grade_response = None
        if grade:
            grade_response = schemas.EssayGradeResponse(
                overall_score=grade.overall_score,
                legal_analysis_score=grade.legal_analysis_score,
                writing_quality_score=grade.writing_quality_score,
                citation_accuracy_score=grade.citation_accuracy_score,
                feedback=grade.feedback,
                point_breakdown=grade.point_breakdown,
                citations=grade.citations
            )
        
        result.append(schemas.Essay(
            id=essay.id,
            user_id=essay.user_id,
            subject=essay.subject,
            prompt=essay.prompt,
            content=essay.content,
            submitted_at=essay.submitted_at,
            grade=grade_response
        ))
    
    return result


@router.get("/{essay_id}", response_model=schemas.Essay)
async def get_essay(
    essay_id: int,
    db: Session = Depends(get_db)
):
    """
    Get a specific essay with its grade.
    """
    essay = db.query(Essay).filter(Essay.id == essay_id).first()
    if not essay:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Essay not found"
        )
    
    grade = db.query(EssayGrade).filter(EssayGrade.essay_id == essay.id).first()
    
    grade_response = None
    if grade:
        grade_response = schemas.EssayGradeResponse(
            overall_score=grade.overall_score,
            legal_analysis_score=grade.legal_analysis_score,
            writing_quality_score=grade.writing_quality_score,
            citation_accuracy_score=grade.citation_accuracy_score,
            feedback=grade.feedback,
            point_breakdown=grade.point_breakdown,
            citations=grade.citations
        )
    
    return schemas.Essay(
        id=essay.id,
        user_id=essay.user_id,
        subject=essay.subject,
        prompt=essay.prompt,
        content=essay.content,
        submitted_at=essay.submitted_at,
        grade=grade_response
    )
