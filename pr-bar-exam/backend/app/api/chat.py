"""
Chat API endpoints.
Chat functionality uses Supabase real-time features, not database models.
Frontend should use Supabase client directly for real-time chat.
"""
from fastapi import APIRouter
from app.schemas import SubjectEnum
from typing import List

router = APIRouter(prefix="/chat", tags=["chat"])


@router.get("/rooms")
async def get_chat_rooms():
    """
    Get all available chat rooms (one per subject).
    Returns basic room info - actual messages handled by Supabase real-time.
    """
    rooms = []
    for subject in SubjectEnum:
        rooms.append({
            "id": subject.value,
            "subject": subject.value,
            "name": f"{subject.value.replace('_', ' ').title()} Discussion",
            "description": f"Discuss {subject.value.replace('_', ' ')} topics with other students"
        })
    return rooms


@router.get("/room/subject/{subject}")
async def get_room_by_subject(subject: SubjectEnum):
    """
    Get chat room info for a specific subject.
    Actual chat messages are handled via Supabase real-time subscriptions in the frontend.
    """
    return {
        "id": subject.value,
        "subject": subject.value,
        "name": f"{subject.value.replace('_', ' ').title()} Discussion",
        "description": f"Discuss {subject.value.replace('_', ' ')} topics with other students",
        "note": "Use Supabase real-time client in frontend to send/receive messages"
    }