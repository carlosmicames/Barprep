"""
Database initialization script.
Run this to set up the database schema and enable pgvector extension.
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from app.core.database import Base, engine
from app.models.models import (
    User, StudyMaterial, DocumentChunk, MCQuestion, MCQResponse,
    Essay, EssayGrade, UserProgress, ChatRoom, ChatMessage, SubjectEnum
)
from sqlalchemy import text


def init_database():
    """Initialize the database schema and extensions."""
    
    print("🔧 Initializing database...")
    
    # Create pgvector extension
    with engine.connect() as conn:
        try:
            conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
            conn.commit()
            print("✅ pgvector extension enabled")
        except Exception as e:
            print(f"⚠️  Warning: Could not enable pgvector: {e}")
            print("   Make sure you have pgvector installed in PostgreSQL")
    
    # Create all tables
    print("📋 Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("✅ All tables created successfully")
    
    # Create default chat rooms
    from sqlalchemy.orm import Session
    from app.core.database import SessionLocal
    
    db = SessionLocal()
    try:
        existing_rooms = db.query(ChatRoom).count()
        if existing_rooms == 0:
            print("💬 Creating default chat rooms...")
            for subject in SubjectEnum:
                room = ChatRoom(
                    subject=subject,
                    name=f"{subject.value.replace('_', ' ').title()}",
                    description=f"Discussion room for {subject.value.replace('_', ' ')}"
                )
                db.add(room)
            db.commit()
            print(f"✅ Created {len(list(SubjectEnum))} chat rooms")
        else:
            print(f"ℹ️  Chat rooms already exist ({existing_rooms} rooms)")
    except Exception as e:
        print(f"❌ Error creating chat rooms: {e}")
        db.rollback()
    finally:
        db.close()
    
    print("\n✨ Database initialization complete!")
    print("\n📝 Next steps:")
    print("   1. Upload study materials via the API")
    print("   2. Process PDFs to create embeddings")
    print("   3. Start generating MCQs and grading essays")


if __name__ == "__main__":
    init_database()
