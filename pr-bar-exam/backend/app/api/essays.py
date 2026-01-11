"""
API endpoints for essay submission and grading.
SIMPLIFIED VERSION - Works without full RAG service implementation.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from app.core.database import get_db
from app.schemas import schemas
from app.models.models import EssaySubmission, EssayPrompt, User, UserProgress
from datetime import datetime

router = APIRouter(prefix="/essays", tags=["essays"])


async def simple_grade_essay(essay_text: str, subject: str, prompt: str) -> dict:
    """
    Placeholder grading function.
    Replace this with actual RAG service call when ready.
    """
    word_count = len(essay_text.split())
    
    # Simple scoring based on length (placeholder)
    score = min(100, (word_count / 500) * 100)
    
    return {
        "overall_score": round(score, 2),
        "legal_analysis_score": round(score * 0.9, 2),
        "writing_quality_score": round(score * 1.0, 2),
        "citation_accuracy_score": round(score * 0.8, 2),
        "feedback": f"Essay received. Word count: {word_count}. Full AI grading coming soon!",
        "point_breakdown": {
            "introduction": "Good",
            "analysis": "Needs work",
            "conclusion": "Adequate"
        },
        "citations": []
    }


@router.post("/submit/{user_id}", response_model=schemas.Essay)
async def submit_essay(
    user_id: int,
    essay_data: schemas.EssaySubmit,
    db: AsyncSession = Depends(get_db)
):
    """
    Submit an essay for AI grading.
    """
    # Verify user exists
    result = await db.execute(select(User).filter(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    try:
        # Grade the essay
        grade_data = await simple_grade_essay(
            essay_text=essay_data.content,
            subject=essay_data.subject.value,
            prompt=essay_data.prompt
        )
        
        # Create essay submission record with grading data
        essay_submission = EssaySubmission(
            user_id=user_id,
            prompt_id=None,  # Using custom prompt
            essay_text=essay_data.content,
            score=grade_data.get("overall_score"),
            feedback={
                "legal_analysis_score": grade_data.get("legal_analysis_score"),
                "writing_quality_score": grade_data.get("writing_quality_score"),
                "citation_accuracy_score": grade_data.get("citation_accuracy_score"),
                "feedback": grade_data.get("feedback", ""),
                "point_breakdown": grade_data.get("point_breakdown", {}),
                "citations": grade_data.get("citations", [])
            },
            word_count=len(essay_data.content.split()),
            submitted_at=datetime.utcnow(),
            graded_at=datetime.utcnow()
        )
        db.add(essay_submission)
        await db.flush()
        
        # Update user progress
        result = await db.execute(
            select(UserProgress).filter(
                UserProgress.user_id == user_id,
                UserProgress.subject == essay_data.subject
            )
        )
        progress = result.scalar_one_or_none()
        
        if progress:
            progress.total_essays += 1
            # Calculate new average
            if progress.avg_essay_score:
                total_score = progress.avg_essay_score * (progress.total_essays - 1)
                progress.avg_essay_score = (total_score + grade_data["overall_score"]) / progress.total_essays
            else:
                progress.avg_essay_score = grade_data["overall_score"]
            progress.last_activity = datetime.utcnow()
        else:
            progress = UserProgress(
                user_id=user_id,
                subject=essay_data.subject,
                total_questions_attempted=0,
                correct_answers=0,
                total_essays=1,
                avg_essay_score=grade_data["overall_score"],
                last_activity=datetime.utcnow()
            )
            db.add(progress)
        
        await db.commit()
        await db.refresh(essay_submission)
        
        # Format response
        return schemas.Essay(
            id=essay_submission.id,
            user_id=essay_submission.user_id,
            subject=essay_data.subject,
            prompt=essay_data.prompt,
            content=essay_submission.essay_text,
            submitted_at=essay_submission.submitted_at,
            grade=schemas.EssayGradeResponse(
                overall_score=essay_submission.score,
                legal_analysis_score=essay_submission.feedback.get("legal_analysis_score"),
                writing_quality_score=essay_submission.feedback.get("writing_quality_score"),
                citation_accuracy_score=essay_submission.feedback.get("citation_accuracy_score"),
                feedback=essay_submission.feedback.get("feedback", ""),
                point_breakdown=essay_submission.feedback.get("point_breakdown", {}),
                citations=essay_submission.feedback.get("citations", [])
            )
        )
    
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to grade essay: {str(e)}"
        )


@router.get("/user/{user_id}", response_model=List[schemas.Essay])
async def get_user_essays(
    user_id: int,
    subject: str = None,
    db: AsyncSession = Depends(get_db)
):
    """
    Get all essays submitted by a user.
    """
    query = select(EssaySubmission).filter(EssaySubmission.user_id == user_id)
    result = await db.execute(query.order_by(EssaySubmission.submitted_at.desc()))
    essays = result.scalars().all()
    
    response = []
    for essay in essays:
        response.append(schemas.Essay(
            id=essay.id,
            user_id=essay.user_id,
            subject=subject or "unknown",  
            prompt="",  
            content=essay.essay_text,
            submitted_at=essay.submitted_at,
            grade=schemas.EssayGradeResponse(
                overall_score=essay.score or 0.0,
                legal_analysis_score=essay.feedback.get("legal_analysis_score") if essay.feedback else None,
                writing_quality_score=essay.feedback.get("writing_quality_score") if essay.feedback else None,
                citation_accuracy_score=essay.feedback.get("citation_accuracy_score") if essay.feedback else None,
                feedback=essay.feedback.get("feedback", "") if essay.feedback else "",
                point_breakdown=essay.feedback.get("point_breakdown", {}) if essay.feedback else {},
                citations=essay.feedback.get("citations", []) if essay.feedback else []
            ) if essay.feedback else None
        ))
    
    return response


@router.get("/{essay_id}", response_model=schemas.Essay)
async def get_essay(
    essay_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Get a specific essay with its grade.
    """
    result = await db.execute(
        select(EssaySubmission).filter(EssaySubmission.id == essay_id)
    )
    essay = result.scalar_one_or_none()
    
    if not essay:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Essay not found"
        )
    
    return schemas.Essay(
        id=essay.id,
        user_id=essay.user_id,
        subject="unknown",
        prompt="",
        content=essay.essay_text,
        submitted_at=essay.submitted_at,
        grade=schemas.EssayGradeResponse(
            overall_score=essay.score or 0.0,
            legal_analysis_score=essay.feedback.get("legal_analysis_score") if essay.feedback else None,
            writing_quality_score=essay.feedback.get("writing_quality_score") if essay.feedback else None,
            citation_accuracy_score=essay.feedback.get("citation_accuracy_score") if essay.feedback else None,
            feedback=essay.feedback.get("feedback", "") if essay.feedback else "",
            point_breakdown=essay.feedback.get("point_breakdown", {}) if essay.feedback else {},
            citations=essay.feedback.get("citations", []) if essay.feedback else []
        ) if essay.feedback else None
    )