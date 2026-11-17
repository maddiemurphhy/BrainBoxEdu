"""
Pydantic schemas: these define the *shape* of data going in and out of
the API (separate from the database models in models.py). FastAPI uses
these to validate requests, generate the interactive /docs page, and
serialize responses to JSON automatically.
"""
from datetime import datetime
from pydantic import BaseModel


class DocumentOut(BaseModel):
    id: int
    filename: str
    confidence_level: str
    confidence_message: str | None
    created_at: datetime

    class Config:
        from_attributes = True  # lets this read straight from a SQLAlchemy object


class QuestionOut(BaseModel):
    id: int
    question_text: str
    answer_text: str
    source_excerpt: str

    class Config:
        from_attributes = True


class GenerateQuestionsRequest(BaseModel):
    num_questions: int = 5
