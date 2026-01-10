"""
Service for processing PDF documents and creating embeddings.
"""
from typing import List, Dict
import PyPDF2
import pdfplumber
from sqlalchemy.orm import Session
from app.models.models import StudyMaterial, DocumentChunk
from app.core.config import settings
from app.services.rag_service import rag_service
import re


class PDFProcessingService:
    """Service for processing PDF documents."""
    
    def __init__(self):
        self.chunk_size = settings.CHUNK_SIZE
        self.chunk_overlap = settings.CHUNK_OVERLAP
    
    def extract_text_from_pdf(self, file_path: str) -> List[Dict[str, any]]:
        """
        Extract text from PDF file page by page.
        Returns list of dicts with page number and text.
        """
        pages_data = []
        
        try:
            with pdfplumber.open(file_path) as pdf:
                for page_num, page in enumerate(pdf.pages, start=1):
                    text = page.extract_text()
                    if text:
                        pages_data.append({
                            "page_number": page_num,
                            "text": text.strip()
                        })
        except Exception as e:
            # Fallback to PyPDF2 if pdfplumber fails
            try:
                with open(file_path, 'rb') as file:
                    pdf_reader = PyPDF2.PdfReader(file)
                    for page_num in range(len(pdf_reader.pages)):
                        page = pdf_reader.pages[page_num]
                        text = page.extract_text()
                        if text:
                            pages_data.append({
                                "page_number": page_num + 1,
                                "text": text.strip()
                            })
            except Exception as inner_e:
                raise ValueError(f"Failed to extract text from PDF: {str(inner_e)}")
        
        return pages_data
    
    def chunk_text(self, text: str, page_number: int) -> List[Dict[str, any]]:
        """
        Split text into overlapping chunks.
        """
        # Clean the text
        text = re.sub(r'\s+', ' ', text).strip()
        
        chunks = []
        start = 0
        text_length = len(text)
        
        while start < text_length:
            end = start + self.chunk_size
            
            # Try to find a sentence boundary
            if end < text_length:
                # Look for period, question mark, or exclamation
                last_period = text.rfind('.', start, end)
                last_question = text.rfind('?', start, end)
                last_exclamation = text.rfind('!', start, end)
                
                boundary = max(last_period, last_question, last_exclamation)
                if boundary > start:
                    end = boundary + 1
            
            chunk = text[start:end].strip()
            if chunk:
                chunks.append({
                    "text": chunk,
                    "page_number": page_number,
                    "chunk_index": len(chunks)
                })
            
            # Move start forward with overlap
            start = end - self.chunk_overlap if end < text_length else text_length
        
        return chunks
    
    def process_pdf_and_create_embeddings(
        self,
        db: Session,
        material_id: int,
        file_path: str
    ) -> int:
        """
        Process a PDF file and create embeddings for all chunks.
        Returns the number of chunks created.
        """
        # Extract text from PDF
        pages_data = self.extract_text_from_pdf(file_path)
        
        total_chunks = 0
        
        for page_data in pages_data:
            # Chunk the page text
            chunks = self.chunk_text(
                page_data["text"],
                page_data["page_number"]
            )
            
            for chunk_data in chunks:
                # Create embedding
                embedding = rag_service.create_embedding(chunk_data["text"])
                
                # Save to database
                chunk = DocumentChunk(
                    material_id=material_id,
                    chunk_text=chunk_data["text"],
                    chunk_index=chunk_data["chunk_index"],
                    page_number=chunk_data["page_number"],
                    embedding=embedding,
                    metadata={
                        "page": chunk_data["page_number"],
                        "length": len(chunk_data["text"])
                    }
                )
                db.add(chunk)
                total_chunks += 1
        
        # Mark material as processed
        material = db.query(StudyMaterial).filter(StudyMaterial.id == material_id).first()
        if material:
            material.processed = True
        
        db.commit()
        
        return total_chunks


# Global PDF processing service instance
pdf_service = PDFProcessingService()
