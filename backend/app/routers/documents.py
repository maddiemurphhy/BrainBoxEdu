"""
Endpoints for uploading a file and checking on it afterwards.
"""
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app import models, schemas
from app.services.extraction import extract_text
from app.services.confidence import check_confidence

router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("/upload", response_model=schemas.DocumentOut)
async def upload_document(file: UploadFile = File(...), db: Session = Depends(get_db)):
    file_bytes = await file.read()

    try:
        text = extract_text(file.filename, file_bytes)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    confidence = check_confidence(text)

    doc = models.Document(
        filename=file.filename,
        extracted_text=text,
        confidence_level=confidence.level,
        confidence_message=confidence.message,
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)

    return doc


@router.get("/{document_id}", response_model=schemas.DocumentOut)
def get_document(document_id: int, db: Session = Depends(get_db)):
    doc = db.query(models.Document).filter(models.Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return doc
