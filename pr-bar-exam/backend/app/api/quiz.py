"""
Admin routes - requires API key + admin UUID.
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from app.core.auth import verify_admin, UserContext
from app.core.database import supabase_admin
from app.services.pdf_service import pdf_service
from app.services.rag_service import rag_service
from app.schemas import (
    SubjectEnum, BLLRuleIngest, BLLRule, AdminStats, UserInfo
)
from typing import List
import tempfile
import os
from datetime import datetime, timedelta

router = APIRouter(prefix="/admin", tags=["admin"])


@router.post("/ingest-shorter", response_model=BLLRuleIngest)
async def ingest_shorter_pdf(
    file: UploadFile = File(...),
    subject: SubjectEnum = Form(...),
    admin: UserContext = Depends(verify_admin)
):
    """
    Ingest a Shorter Bar Review PDF and extract BLL rules.
    
    Parses tables from the PDF to extract:
    - Rule Name
    - Article #
    - Description
    
    Saves extracted rules to Supabase.
    """
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files allowed")
    
    errors = []
    rules_extracted = 0
    rules_created = 0
    
    # Save file temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
        content = await file.read()
        temp_file.write(content)
        temp_path = temp_file.name
    
    try:
        # Parse PDF for BLL rules
        bll_rules = pdf_service.parse_shorter_pdf(temp_path, subject)
        rules_extracted = len(bll_rules)
        
        # Save rules to database
        for rule in bll_rules:
            try:
                supabase_admin.table("bll_rules").insert({
                    "subject": rule.subject.value,
                    "rule_name": rule.rule_name,
                    "article_number": rule.article_number,
                    "description": rule.description,
                    "source_pdf": rule.source_pdf,
                    "page_number": rule.page_number
                }).execute()
                rules_created += 1
            except Exception as e:
                errors.append(f"Failed to save rule '{rule.rule_name}': {str(e)}")
        
        # Also create embeddings for RAG
        pages = pdf_service.extract_text_from_pdf(temp_path)
        for page in pages:
            chunks = pdf_service._chunk_text(page["text"], page["page_number"])
            for chunk in chunks:
                try:
                    rag_service.store_document_chunk(
                        subject=subject,
                        chunk_text=chunk["text"],
                        page_number=chunk["page_number"],
                        source_file=file.filename,
                        metadata={"type": "shorter", "chunk_index": chunk["chunk_index"]}
                    )
                except Exception as e:
                    errors.append(f"Failed to create embedding: {str(e)}")
        
    except Exception as e:
        errors.append(f"PDF processing error: {str(e)}")
    finally:
        # Clean up temp file
        os.unlink(temp_path)
    
    return BLLRuleIngest(
        subject=subject,
        rules_extracted=rules_extracted,
        rules_created=rules_created,
        errors=errors[:10]  # Limit errors in response
    )


@router.post("/upload-statute")
async def upload_statute_pdf(
    file: UploadFile = File(...),
    subject: SubjectEnum = Form(...),
    title: str = Form(...),
    admin: UserContext = Depends(verify_admin)
):
    """
    Upload a Civil Code statute PDF and process for RAG.
    """
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files allowed")
    
    # Save to Supabase Storage
    content = await file.read()
    file_path = f"statutes/{subject.value}/{file.filename}"
    
    try:
        # Upload to Supabase Storage
        storage_result = supabase_admin.storage.from_("study-materials").upload(
            file_path,
            content,
            {"content-type": "application/pdf"}
        )
        
        # Create database record
        material_result = supabase_admin.table("study_materials").insert({
            "subject": subject.value,
            "title": title,
            "file_path": file_path,
            "is_shorter": False,
            "is_processed": False,
            "uploaded_at": datetime.utcnow().isoformat()
        }).execute()
        
        material_id = material_result.data[0]["id"]
        
        # Process PDF for RAG (in background ideally)
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
            temp_file.write(content)
            temp_path = temp_file.name
        
        try:
            pages = pdf_service.extract_text_from_pdf(temp_path)
            chunks_created = 0
            
            for page in pages:
                chunks = pdf_service._chunk_text(page["text"], page["page_number"])
                for chunk in chunks:
                    rag_service.store_document_chunk(
                        subject=subject,
                        chunk_text=chunk["text"],
                        page_number=chunk["page_number"],
                        source_file=file.filename,
                        metadata={"material_id": material_id, "type": "statute"}
                    )
                    chunks_created += 1
            
            # Mark as processed
            supabase_admin.table("study_materials").update({
                "is_processed": True
            }).eq("id", material_id).execute()
            
        finally:
            os.unlink(temp_path)
        
        return {
            "message": "Statute uploaded and processed",
            "material_id": material_id,
            "file_path": file_path,
            "chunks_created": chunks_created
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to upload statute: {str(e)}"
        )


@router.get("/stats", response_model=AdminStats)
async def get_admin_stats(
    admin: UserContext = Depends(verify_admin)
):
    """Get admin dashboard statistics."""
    
    # Total users
    users_result = supabase_admin.auth.admin.list_users()
    total_users = len(users_result)
    
    # Total quiz sessions
    sessions_result = supabase_admin.table("quiz_sessions").select(
        "id", count="exact"
    ).execute()
    total_sessions = sessions_result.count or 0
    
    # Total BLL rules
    rules_result = supabase_admin.table("bll_rules").select(
        "id", count="exact"
    ).execute()
    total_rules = rules_result.count or 0
    
    # Total essays
    essays_result = supabase_admin.table("essays").select(
        "id", count="exact"
    ).execute()
    total_essays = essays_result.count or 0
    
    # Active users this week
    week_ago = (datetime.utcnow() - timedelta(days=7)).isoformat()
    active_result = supabase_admin.table("quiz_sessions").select(
        "user_id"
    ).gte("started_at", week_ago).execute()
    
    active_users = len(set(s["user_id"] for s in (active_result.data or [])))
    
    return AdminStats(
        total_users=total_users,
        total_quiz_sessions=total_sessions,
        total_bll_rules=total_rules,
        total_essays=total_essays,
        active_users_this_week=active_users
    )


@router.get("/users", response_model=List[UserInfo])
async def list_users(
    limit: int = 50,
    admin: UserContext = Depends(verify_admin)
):
    """List all users (admin only)."""
    
    users = supabase_admin.auth.admin.list_users()
    
    result = []
    for user in users[:limit]:
        # Get quiz session count
        sessions_result = supabase_admin.table("quiz_sessions").select(
            "id", count="exact"
        ).eq("user_id", user.id).execute()
        
        result.append(UserInfo(
            id=user.id,
            email=user.email or "",
            created_at=user.created_at,
            last_sign_in=user.last_sign_in_at,
            quiz_sessions_count=sessions_result.count or 0
        ))
    
    return result


@router.get("/bll-rules/{subject}", response_model=List[BLLRule])
async def get_bll_rules(
    subject: SubjectEnum,
    admin: UserContext = Depends(verify_admin)
):
    """Get all BLL rules for a subject (admin view)."""
    
    result = supabase_admin.table("bll_rules").select("*").eq(
        "subject", subject.value
    ).order("created_at", desc=True).execute()
    
    return [
        BLLRule(
            id=r["id"],
            subject=SubjectEnum(r["subject"]),
            rule_name=r["rule_name"],
            article_number=r.get("article_number"),
            description=r["description"],
            source_pdf=r.get("source_pdf"),
            page_number=r.get("page_number"),
            created_at=datetime.fromisoformat(r["created_at"])
        )
        for r in (result.data or [])
    ]


@router.delete("/bll-rules/{rule_id}")
async def delete_bll_rule(
    rule_id: str,
    admin: UserContext = Depends(verify_admin)
):
    """Delete a BLL rule."""
    
    supabase_admin.table("bll_rules").delete().eq("id", rule_id).execute()
    
    return {"message": "Rule deleted"}


@router.delete("/reset-subject/{subject}")
async def reset_subject_data(
    subject: SubjectEnum,
    admin: UserContext = Depends(verify_admin)
):
    """
    DANGEROUS: Delete all data for a subject.
    Removes BLL rules, document chunks, and quiz data.
    """
    
    # Delete BLL rules
    supabase_admin.table("bll_rules").delete().eq(
        "subject", subject.value
    ).execute()
    
    # Delete document chunks
    supabase_admin.table("document_chunks").delete().eq(
        "subject", subject.value
    ).execute()
    
    # Delete quiz questions for this subject
    supabase_admin.table("quiz_questions").delete().eq(
        "subject", subject.value
    ).execute()
    
    return {
        "message": f"All data for {subject.value} has been deleted",
        "subject": subject.value
    }