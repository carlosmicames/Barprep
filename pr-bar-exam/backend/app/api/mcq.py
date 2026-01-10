"""
API endpoints for MCQ operations.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.schemas import schemas
from app.models.models import MCQuestion, MCQResponse, User, UserProgress, SubjectEnum
from app.services.rag_service import rag_service
from datetime import datetime

router = APIRouter(prefix="/mcq", tags=["mcq"])


@router.post("/generate", response_model=List[schemas.MCQuestion])
async def generate_mcqs(
    request: schemas.MCQGenerateRequest,
    db: Session = Depends(get_db)
):
    """
    Generate MCQs from study materials using AI.
    """
    try:
        # Generate questions using RAG service
        generated_questions = rag_service.generate_mcqs(
            db=db,
            subject=request.subject,
            num_questions=request.num_questions,
            difficulty=request.difficulty or "medium"
        )
        
        # Save questions to database
        saved_questions = []
        for q in generated_questions:
            mcq = MCQuestion(
                subject=request.subject,
                question_text=q["question"],
                option_a=q["options"]["A"],
                option_b=q["options"]["B"],
                option_c=q["options"]["C"],
                option_d=q["options"]["D"],
                correct_answer=q["correct_answer"],
                explanation=q.get("explanation"),
                difficulty=request.difficulty or "medium"
            )
            db.add(mcq)
            db.flush()
            saved_questions.append(mcq)
        
        db.commit()
        
        # Refresh to get all fields
        for q in saved_questions:
            db.refresh(q)
        
        return saved_questions
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate MCQs: {str(e)}"
        )


@router.get("/questions/{subject}", response_model=List[schemas.MCQWithoutAnswer])
async def get_questions_by_subject(
    subject: SubjectEnum,
    limit: int = 20,
    difficulty: str = None,
    db: Session = Depends(get_db)
):
    """
    Get MCQ questions for a subject (without revealing answers).
    """
    query = db.query(MCQuestion).filter(MCQuestion.subject == subject)
    
    if difficulty:
        query = query.filter(MCQuestion.difficulty == difficulty)
    
    questions = query.limit(limit).all()
    
    # Format without revealing correct answer
    result = []
    for q in questions:
        result.append(schemas.MCQWithoutAnswer(
            id=q.id,
            subject=q.subject,
            question_text=q.question_text,
            options=[
                schemas.MCQOption(label="A", text=q.option_a),
                schemas.MCQOption(label="B", text=q.option_b),
                schemas.MCQOption(label="C", text=q.option_c),
                schemas.MCQOption(label="D", text=q.option_d),
            ],
            difficulty=q.difficulty
        ))
    
    return result


@router.post("/submit/{user_id}", response_model=schemas.MCQResponseResult)
async def submit_mcq_response(
    user_id: int,
    response: schemas.MCQResponseCreate,
    db: Session = Depends(get_db)
):
    """
    Submit an MCQ response and get immediate feedback.
    """
    # Get the question
    question = db.query(MCQuestion).filter(MCQuestion.id == response.question_id).first()
    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Question not found"
        )
    
    # Check if answer is correct
    is_correct = response.selected_answer.upper() == question.correct_answer.upper()
    
    # Save response
    mcq_response = MCQResponse(
        user_id=user_id,
        question_id=response.question_id,
        selected_answer=response.selected_answer.upper(),
        is_correct=is_correct,
        time_spent_seconds=response.time_spent_seconds
    )
    db.add(mcq_response)
    
    # Update user progress
    progress = db.query(UserProgress).filter(
        UserProgress.user_id == user_id,
        UserProgress.subject == question.subject
    ).first()
    
    if progress:
        progress.total_mcqs_attempted += 1
        if is_correct:
            progress.total_mcqs_correct += 1
        progress.last_activity = datetime.now()
    else:
        progress = UserProgress(
            user_id=user_id,
            subject=question.subject,
            total_mcqs_attempted=1,
            total_mcqs_correct=1 if is_correct else 0,
            total_essays_submitted=0
        )
        db.add(progress)
    
    db.commit()
    
    return schemas.MCQResponseResult(
        is_correct=is_correct,
        correct_answer=question.correct_answer,
        explanation=question.explanation,
        selected_answer=response.selected_answer.upper()
    )


@router.get("/stats/{user_id}/{subject}")
async def get_mcq_stats(
    user_id: int,
    subject: SubjectEnum,
    db: Session = Depends(get_db)
):
    """
    Get MCQ statistics for a user and subject.
    """
    progress = db.query(UserProgress).filter(
        UserProgress.user_id == user_id,
        UserProgress.subject == subject
    ).first()
    
    if not progress:
        return {
            "total_attempted": 0,
            "total_correct": 0,
            "accuracy": 0.0
        }
    
    accuracy = (progress.total_mcqs_correct / progress.total_mcqs_attempted * 100) if progress.total_mcqs_attempted > 0 else 0.0
    
    return {
        "total_attempted": progress.total_mcqs_attempted,
        "total_correct": progress.total_mcqs_correct,
        "accuracy": round(accuracy, 2)
    }
