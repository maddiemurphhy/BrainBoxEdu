"""
Turns an uploaded file into plain text, whatever format it came in as.
This is the first step of the pipeline: upload -> EXTRACT TEXT -> check
confidence -> generate questions.
"""
from pypdf import PdfReader
from docx import Document as DocxDocument
from pptx import Presentation
import io


def extract_text(filename: str, file_bytes: bytes) -> str:
    """
    Looks at the file extension and routes to the right extractor.
    Raises ValueError for anything we don't support yet.
    """
    lower = filename.lower()

    if lower.endswith(".pdf"):
        return _extract_pdf(file_bytes)
    elif lower.endswith(".docx"):
        return _extract_docx(file_bytes)
    elif lower.endswith(".pptx"):
        return _extract_pptx(file_bytes)
    elif lower.endswith(".txt"):
        return file_bytes.decode("utf-8", errors="ignore")
    else:
        raise ValueError(
            f"Unsupported file type for '{filename}'. "
            "Supported: .pdf, .docx, .pptx, .txt"
        )


def _extract_pdf(file_bytes: bytes) -> str:
    reader = PdfReader(io.BytesIO(file_bytes))
    pages_text = [page.extract_text() or "" for page in reader.pages]
    return "\n\n".join(pages_text)


def _extract_docx(file_bytes: bytes) -> str:
    doc = DocxDocument(io.BytesIO(file_bytes))
    return "\n".join(p.text for p in doc.paragraphs)


def _extract_pptx(file_bytes: bytes) -> str:
    prs = Presentation(io.BytesIO(file_bytes))
    slides_text = []
    for slide in prs.slides:
        for shape in slide.shapes:
            if hasattr(shape, "text") and shape.text:
                slides_text.append(shape.text)
    return "\n".join(slides_text)
