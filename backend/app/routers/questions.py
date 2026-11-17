"""
Endpoint that turns an already-uploaded document into study questions.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import anthropic

from app.database import get_db
from app import models, schemas
from app.services.ai_client import generate_questions

router = APIRouter(prefix="/documents", tags=["questions"])


@router.post("/{document_id}/questions/generate", response_model=list[schemas.QuestionOut])
def generate_questions_for_document(
    document_id: int,
    request: schemas.GenerateQuestionsRequest,
    db: Session = Depends(get_db),
):
    doc = db.query(models.Document).filter(models.Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    try:
        generated = generate_questions(doc.extracted_text, request.num_questions)
    except anthropic.AuthenticationError:
        raise HTTPException(
            status_code=502,
            detail="The Anthropic API key is missing or invalid. Check ANTHROPIC_API_KEY in your .env file.",
        )
    except anthropic.APIError as e:
        raise HTTPException(status_code=502, detail=f"The AI service call failed: {e}")

    saved_questions = []
    for q in generated:
        question_row = models.Question(
            document_id=doc.id,
            question_text=q["question"],
            answer_text=q["answer"],
            source_excerpt=q["source_excerpt"],
        )
        db.add(question_row)
        saved_questions.append(question_row)

    db.commit()
    for q in saved_questions:
        db.refresh(q)

    return saved_questions


@router.get("/{document_id}/questions", response_model=list[schemas.QuestionOut])
def get_questions_for_document(document_id: int, db: Session = Depends(get_db)):
    doc = db.query(models.Document).filter(models.Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return doc.questions
