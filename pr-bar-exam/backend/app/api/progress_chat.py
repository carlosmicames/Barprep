"""
API endpoints for progress tracking and chat.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.schemas import schemas
from app.models.models import UserProgress, User, ChatRoom, ChatMessage, SubjectEnum
from datetime import datetime

progress_router = APIRouter(prefix="/progress", tags=["progress"])
chat_router = APIRouter(prefix="/chat", tags=["chat"])


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
        accuracy = (progress.total_mcqs_correct / progress.total_mcqs_attempted * 100) if progress.total_mcqs_attempted > 0 else 0.0
        
        subjects_progress.append(schemas.SubjectProgress(
            subject=progress.subject,
            total_mcqs_attempted=progress.total_mcqs_attempted,
            total_mcqs_correct=progress.total_mcqs_correct,
            accuracy_percentage=round(accuracy, 2),
            total_essays_submitted=progress.total_essays_submitted,
            average_essay_score=progress.average_essay_score,
            last_activity=progress.last_activity
        ))
        
        total_attempted += progress.total_mcqs_attempted
        total_correct += progress.total_mcqs_correct
    
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
    
    accuracy = (progress.total_mcqs_correct / progress.total_mcqs_attempted * 100) if progress.total_mcqs_attempted > 0 else 0.0
    
    return schemas.SubjectProgress(
        subject=progress.subject,
        total_mcqs_attempted=progress.total_mcqs_attempted,
        total_mcqs_correct=progress.total_mcqs_correct,
        accuracy_percentage=round(accuracy, 2),
        total_essays_submitted=progress.total_essays_submitted,
        average_essay_score=progress.average_essay_score,
        last_activity=progress.last_activity
    )


# ==================== CHAT ENDPOINTS ====================

@chat_router.get("/rooms", response_model=List[schemas.ChatRoom])
async def get_chat_rooms(db: Session = Depends(get_db)):
    """
    Get all chat rooms (one per subject).
    """
    rooms = db.query(ChatRoom).all()
    
    # If rooms don't exist, create them
    if not rooms:
        for subject in SubjectEnum:
            room = ChatRoom(
                subject=subject,
                name=f"{subject.value.title()} Discussion",
                description=f"Discuss {subject.value} topics with other students"
            )
            db.add(room)
        db.commit()
        rooms = db.query(ChatRoom).all()
    
    return rooms


@chat_router.get("/room/{room_id}/messages", response_model=List[schemas.ChatMessage])
async def get_room_messages(
    room_id: int,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """
    Get recent messages from a chat room.
    """
    messages = db.query(ChatMessage).filter(
        ChatMessage.room_id == room_id
    ).order_by(ChatMessage.created_at.desc()).limit(limit).all()
    
    # Reverse to get chronological order
    messages.reverse()
    
    return messages


@chat_router.post("/message/{user_id}", response_model=schemas.ChatMessage)
async def send_message(
    user_id: int,
    message_data: schemas.ChatMessageCreate,
    db: Session = Depends(get_db)
):
    """
    Send a message to a chat room.
    """
    # Verify user exists
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Verify room exists
    room = db.query(ChatRoom).filter(ChatRoom.id == message_data.room_id).first()
    if not room:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat room not found"
        )
    
    # Create message
    message = ChatMessage(
        room_id=message_data.room_id,
        user_id=user_id,
        message=message_data.message
    )
    db.add(message)
    db.commit()
    db.refresh(message)
    
    return message


@chat_router.get("/room/subject/{subject}", response_model=schemas.ChatRoom)
async def get_room_by_subject(
    subject: SubjectEnum,
    db: Session = Depends(get_db)
):
    """
    Get chat room for a specific subject.
    """
    room = db.query(ChatRoom).filter(ChatRoom.subject == subject).first()
    
    if not room:
        # Create room if it doesn't exist
        room = ChatRoom(
            subject=subject,
            name=f"{subject.value.title()} Discussion",
            description=f"Discuss {subject.value} topics with other students"
        )
        db.add(room)
        db.commit()
        db.refresh(room)
    
    return room
