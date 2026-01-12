"""
Public API endpoints - no authentication required.
"""
from fastapi import APIRouter
from app.schemas import SubjectEnum
from typing import List

router = APIRouter(tags=["public"])


@router.get("/ping")
async def ping():
    """Simple ping endpoint to check if API is running."""
    return {"message": "pong"}


@router.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}


@router.get("/subjects", response_model=List[dict])
async def get_subjects():
    """
    Get all available bar exam subjects.
    No authentication required.
    """
    subjects = [
        {
            "value": subject.value,
            "name": subject.name.replace("_", " ").title(),
            "description": _get_subject_description(subject)
        }
        for subject in SubjectEnum
    ]
    return subjects


def _get_subject_description(subject: SubjectEnum) -> str:
    """Get description for each subject."""
    descriptions = {
        SubjectEnum.CONSTITUTIONAL: "Constitutional Law and Civil Rights",
        SubjectEnum.CRIMINAL: "Criminal Law and Procedure",
        SubjectEnum.EVIDENCE: "Rules of Evidence",
        SubjectEnum.REAL_ESTATE_REGISTRY: "Property and Real Estate Registry Law",
        SubjectEnum.FAMILY: "Family Law and Domestic Relations",
        SubjectEnum.SUCCESSION: "Wills, Trusts, and Estates",
        SubjectEnum.OBLIGATIONS_CONTRACTS: "Obligations and Contracts",
        SubjectEnum.CIVIL_PROCEDURE: "Civil Procedure",
        SubjectEnum.TORTS: "Tort Law",
        SubjectEnum.COMMERCIAL: "Commercial Law",
        SubjectEnum.CORPORATIONS: "Corporate Law",
        SubjectEnum.LABOR: "Labor and Employment Law",
        SubjectEnum.ADMINISTRATIVE: "Administrative Law"
    }
    return descriptions.get(subject, "")