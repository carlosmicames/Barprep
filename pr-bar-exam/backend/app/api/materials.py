"""
API endpoints for study materials upload and management.
"""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.core.config import settings
from app.schemas import schemas
from app.models.models import StudyMaterial, User, SubjectEnum
from app.services.pdf_service import pdf_service
from app.services.blob_service import blob_service
import os
import shutil
from pathlib import Path
import tempfile

router = APIRouter(prefix="/materials", tags=["study-materials"])

# Storage directory for uploaded files
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


@router.post("/upload/{user_id}", response_model=schemas.StudyMaterial)
async def upload_study_material(
    user_id: int,
    file: UploadFile = File(...),
    subject: SubjectEnum = Form(...),
    title: str = Form(...),
    is_official: bool = Form(False),
    db: Session = Depends(get_db)
):
    """
    Upload a study material (PDF or DOCX) and process it for RAG.
    """
    # Verify user exists
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Check file extension
    file_ext = os.path.splitext(file.filename)[1].lower()
    if file_ext not in settings.allowed_extensions_list:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type {file_ext} not allowed. Allowed types: {settings.ALLOWED_EXTENSIONS}"
        )
    
    # Check file size
    file.file.seek(0, 2)  # Seek to end
    file_size = file.file.tell()
    file.file.seek(0)  # Reset to beginning
    
    if file_size > settings.MAX_UPLOAD_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File too large. Max size: {settings.MAX_UPLOAD_SIZE / 1024 / 1024}MB"
        )
    
    try:
        # Use Vercel Blob Storage if available, otherwise local storage
        use_blob = blob_service is not None and os.getenv("VERCEL")

        if use_blob:
            # Upload to Vercel Blob Storage
            blob_filename = f"{user_id}_{subject.value}_{file.filename}"
            blob_result = await blob_service.upload_file(
                file=file.file,
                filename=blob_filename,
                content_type=file.content_type or "application/pdf"
            )
            file_path_str = blob_result["url"]
            download_url = blob_result.get("downloadUrl", blob_result["url"])

            # For PDF processing, download to temp file
            if file_ext == ".pdf":
                temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
                temp_path = temp_file.name
                file.file.seek(0)
                with open(temp_path, "wb") as buffer:
                    shutil.copyfileobj(file.file, buffer)
                processing_path = temp_path
            else:
                processing_path = None
        else:
            # Save file locally
            file_path = UPLOAD_DIR / f"{user_id}_{subject.value}_{file.filename}"
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            file_path_str = str(file_path)
            processing_path = str(file_path)

        # Create database record
        material = StudyMaterial(
            user_id=user_id,
            subject=subject,
            title=title,
            file_path=file_path_str,
            file_type=file_ext.replace(".", ""),
            is_official=is_official,
            processed=False
        )
        db.add(material)
        db.commit()
        db.refresh(material)

        # Process PDF in background (in production, use Celery or similar)
        if file_ext == ".pdf" and processing_path:
            try:
                chunks_created = pdf_service.process_pdf_and_create_embeddings(
                    db=db,
                    material_id=material.id,
                    file_path=processing_path
                )
                print(f"Created {chunks_created} chunks for material {material.id}")

                # Clean up temp file if using blob storage
                if use_blob:
                    os.unlink(processing_path)
            except Exception as e:
                print(f"Error processing PDF: {str(e)}")
                # Clean up temp file on error
                if use_blob and processing_path and os.path.exists(processing_path):
                    os.unlink(processing_path)
                # Don't fail the upload, just mark as not processed
                material.processed = False
                db.commit()

        db.refresh(material)
        return material
    
    except Exception as e:
        db.rollback()
        # Clean up file if database operation failed
        if file_path.exists():
            file_path.unlink()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload material: {str(e)}"
        )


@router.get("/subject/{subject}", response_model=List[schemas.StudyMaterial])
async def get_materials_by_subject(
    subject: SubjectEnum,
    db: Session = Depends(get_db)
):
    """
    Get all study materials for a subject.
    """
    materials = db.query(StudyMaterial).filter(
        StudyMaterial.subject == subject
    ).order_by(StudyMaterial.is_official.desc(), StudyMaterial.uploaded_at.desc()).all()
    
    return materials


@router.get("/user/{user_id}", response_model=List[schemas.StudyMaterial])
async def get_user_materials(
    user_id: int,
    db: Session = Depends(get_db)
):
    """
    Get all study materials uploaded by a user.
    """
    materials = db.query(StudyMaterial).filter(
        StudyMaterial.user_id == user_id
    ).order_by(StudyMaterial.uploaded_at.desc()).all()
    
    return materials


@router.delete("/{material_id}")
async def delete_material(
    material_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete a study material and its file.
    """
    material = db.query(StudyMaterial).filter(StudyMaterial.id == material_id).first()
    if not material:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Material not found"
        )
    
    # Delete file
    file_path = Path(material.file_path)
    if file_path.exists():
        file_path.unlink()
    
    # Delete from database (chunks will be deleted via cascade)
    db.delete(material)
    db.commit()
    
    return {"message": "Material deleted successfully"}
