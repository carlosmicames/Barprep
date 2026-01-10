"""
RAG (Retrieval-Augmented Generation) service using OpenAI and pgvector.
"""
from typing import List, Dict, Any, Optional
import openai
from sqlalchemy.orm import Session
from sqlalchemy import select, text
from app.core.config import settings
from app.models.models import DocumentChunk, StudyMaterial, SubjectEnum
import tiktoken
import json


class RAGService:
    """Service for RAG operations including embeddings and retrieval."""
    
    def __init__(self):
        self.client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = settings.OPENAI_MODEL
        self.embedding_model = settings.OPENAI_EMBEDDING_MODEL
        self.encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")
    
    def create_embedding(self, text: str) -> List[float]:
        """Create embedding for a piece of text."""
        response = self.client.embeddings.create(
            model=self.embedding_model,
            input=text
        )
        return response.data[0].embedding
    
    def retrieve_relevant_chunks(
        self,
        db: Session,
        query: str,
        subject: SubjectEnum,
        top_k: int = 5,
        similarity_threshold: float = 0.7
    ) -> List[Dict[str, Any]]:
        """
        Retrieve most relevant document chunks for a query using vector similarity.
        """
        # Create query embedding
        query_embedding = self.create_embedding(query)
        
        # Use pgvector for similarity search
        # Note: This requires pgvector extension to be installed in PostgreSQL
        query_text = text("""
            SELECT 
                dc.id,
                dc.chunk_text,
                dc.page_number,
                sm.title as source_title,
                sm.file_type,
                (dc.embedding <=> :query_embedding::vector) as distance
            FROM document_chunks dc
            JOIN study_materials sm ON dc.material_id = sm.id
            WHERE sm.subject = :subject
            ORDER BY dc.embedding <=> :query_embedding::vector
            LIMIT :top_k
        """)
        
        results = db.execute(
            query_text,
            {
                "query_embedding": str(query_embedding),
                "subject": subject.value,
                "top_k": top_k
            }
        ).fetchall()
        
        # Filter by similarity threshold (distance < threshold means high similarity)
        filtered_results = []
        for row in results:
            similarity = 1 - row.distance  # Convert distance to similarity
            if similarity >= similarity_threshold:
                filtered_results.append({
                    "text": row.chunk_text,
                    "source": row.source_title,
                    "page_number": row.page_number,
                    "similarity_score": similarity
                })
        
        return filtered_results
    
    def generate_mcqs(
        self,
        db: Session,
        subject: SubjectEnum,
        num_questions: int = 10,
        difficulty: str = "medium"
    ) -> List[Dict[str, Any]]:
        """
        Generate MCQs from study materials using OpenAI.
        """
        # Get representative chunks from the subject
        all_chunks = db.query(DocumentChunk).join(StudyMaterial).filter(
            StudyMaterial.subject == subject
        ).limit(20).all()
        
        if not all_chunks:
            raise ValueError(f"No study materials found for subject: {subject.value}")
        
        # Combine chunks for context
        context = "\n\n".join([chunk.chunk_text for chunk in all_chunks[:10]])
        
        prompt = f"""You are an expert in Puerto Rico law, specifically in {subject.value}.

Based on the following legal content, generate {num_questions} multiple-choice questions at {difficulty} difficulty level.

LEGAL CONTENT:
{context}

INSTRUCTIONS:
1. Generate {num_questions} multiple-choice questions with 4 options each (A, B, C, D)
2. Questions should test understanding of legal concepts, not just memorization
3. Difficulty level: {difficulty}
4. Include a brief explanation for the correct answer
5. Format your response as a JSON array of objects

REQUIRED JSON FORMAT:
[
  {{
    "question": "Question text here?",
    "options": {{
      "A": "Option A text",
      "B": "Option B text",
      "C": "Option C text",
      "D": "Option D text"
    }},
    "correct_answer": "A",
    "explanation": "Brief explanation of why A is correct"
  }}
]

Generate the questions now:"""
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a Puerto Rico law professor creating bar exam practice questions."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=3000
        )
        
        try:
            questions = json.loads(response.choices[0].message.content)
            return questions
        except json.JSONDecodeError:
            # If JSON parsing fails, try to extract JSON from the response
            content = response.choices[0].message.content
            # Try to find JSON array in the response
            start = content.find('[')
            end = content.rfind(']') + 1
            if start != -1 and end != 0:
                questions = json.loads(content[start:end])
                return questions
            raise ValueError("Failed to parse MCQ response from OpenAI")
    
    def grade_essay(
        self,
        db: Session,
        essay_content: str,
        subject: SubjectEnum,
        prompt: str
    ) -> Dict[str, Any]:
        """
        Grade an essay using RAG to ensure grading is based on provided legal materials.
        """
        # Retrieve relevant legal sources
        relevant_chunks = self.retrieve_relevant_chunks(
            db=db,
            query=prompt + " " + essay_content,
            subject=subject,
            top_k=8
        )
        
        if not relevant_chunks:
            raise ValueError(f"No reference materials found for subject: {subject.value}")
        
        # Prepare context from retrieved chunks
        legal_context = "\n\n---\n\n".join([
            f"SOURCE: {chunk['source']} (Page {chunk.get('page_number', 'N/A')})\n{chunk['text']}"
            for chunk in relevant_chunks
        ])
        
        grading_prompt = f"""You are a Puerto Rico bar exam grader. Grade this essay STRICTLY based on the provided legal materials.

PROMPT:
{prompt}

STUDENT ESSAY:
{essay_content}

REFERENCE LEGAL MATERIALS:
{legal_context}

GRADING INSTRUCTIONS:
1. You MUST ONLY use the provided reference materials for grading
2. Cite specific sources when evaluating legal accuracy
3. Grade on a 0-100 scale with breakdown:
   - Legal Analysis (40 points): Correct identification and application of legal principles
   - Citation Accuracy (30 points): Proper use of legal sources
   - Writing Quality (30 points): Organization, clarity, and coherence

4. Provide specific feedback with citations from the reference materials
5. List all citations used in your evaluation

FORMAT YOUR RESPONSE AS JSON:
{{
  "overall_score": 85.5,
  "legal_analysis_score": 35.0,
  "citation_accuracy_score": 25.0,
  "writing_quality_score": 25.5,
  "feedback": "Detailed feedback here...",
  "point_breakdown": {{
    "strengths": ["point 1", "point 2"],
    "weaknesses": ["point 1", "point 2"],
    "suggestions": ["suggestion 1", "suggestion 2"]
  }},
  "citations": [
    {{"source": "Source name", "page": "123", "quote": "Relevant quote"}}
  ]
}}

Grade the essay now:"""
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": "You are a strict Puerto Rico bar exam grader. You ONLY use provided reference materials for grading. Never use external knowledge."
                },
                {"role": "user", "content": grading_prompt}
            ],
            temperature=0.3,  # Lower temperature for consistent grading
            max_tokens=2000
        )
        
        try:
            grade_data = json.loads(response.choices[0].message.content)
            return grade_data
        except json.JSONDecodeError:
            # Try to extract JSON
            content = response.choices[0].message.content
            start = content.find('{')
            end = content.rfind('}') + 1
            if start != -1 and end != 0:
                grade_data = json.loads(content[start:end])
                return grade_data
            raise ValueError("Failed to parse grading response from OpenAI")


# Global RAG service instance
rag_service = RAGService()
