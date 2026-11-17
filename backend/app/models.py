"""
Database tables, defined as Python classes (this is what "ORM" means --
SQLAlchemy turns these classes into SQL tables and rows into objects
for you, so you mostly don't write raw SQL).
"""
import datetime

from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Float
from sqlalchemy.orm import relationship

from app.database import Base


class Document(Base):
    """One uploaded file (lecture notes, slides, a syllabus chunk, etc.)."""

    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    extracted_text = Column(Text, nullable=False)

    # Confidence check results (see app/services/confidence.py).
    # confidence_level is one of: "high", "low"
    confidence_level = Column(String, default="high")
    confidence_message = Column(String, nullable=True)

    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    questions = relationship("Question", back_populates="document", cascade="all, delete-orphan")


class Question(Base):
    """One AI-generated study question tied back to a Document."""

    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False)

    question_text = Column(Text, nullable=False)
    answer_text = Column(Text, nullable=False)

    # The verbatim-ish snippet from the uploaded material that this
    # question is grounded in. Shown in the UI next to the question so
    # the student can sanity-check it. If the model can't produce one,
    # we don't save the question at all (see ai_client.py).
    source_excerpt = Column(Text, nullable=False)

    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    document = relationship("Document", back_populates="questions")
