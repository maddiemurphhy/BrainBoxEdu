"""
A deliberately simple heuristic for risk #2 from the project plan: the
AI shouldn't silently guess when the uploaded material is too sparse
or garbled to generate good questions from. This isn't trying to be
clever -- it's a handful of cheap checks that catch the obvious bad
cases (near-empty extraction, mostly-garbage characters) so the API can
tell the frontend "this didn't come through well" instead of quietly
generating a full question set from almost nothing.

You can make this smarter later (e.g. checking sentence structure, or
asking the AI itself to rate its own confidence) -- this is a floor,
not a ceiling.
"""
import re
from dataclasses import dataclass


@dataclass
class ConfidenceResult:
    level: str  # "high" or "low"
    message: str | None


MIN_CHARACTERS = 300          # below this, there's just not much to work with
MIN_WORDS = 50
MAX_GARBLED_RATIO = 0.3       # fraction of non-alphanumeric "junk" characters


def check_confidence(extracted_text: str) -> ConfidenceResult:
    text = extracted_text.strip()

    if len(text) < MIN_CHARACTERS:
        return ConfidenceResult(
            level="low",
            message=(
                "We could only pull a small amount of text from this file "
                "(it may be a scanned image, a mostly-blank file, or an "
                "unusual format). Try a clearer version if you have one."
            ),
        )

    word_count = len(text.split())
    if word_count < MIN_WORDS:
        return ConfidenceResult(
            level="low",
            message=(
                "This file doesn't have much readable text in it. "
                "Questions generated from it may be thin or off-base."
            ),
        )

    # Rough "garbled OCR / binary junk" check: count characters that are
    # not letters, numbers, common punctuation, or whitespace.
    junk_chars = re.findall(r"[^a-zA-Z0-9\s.,;:!?'\"()\-\n]", text)
    junk_ratio = len(junk_chars) / max(len(text), 1)
    if junk_ratio > MAX_GARBLED_RATIO:
        return ConfidenceResult(
            level="low",
            message=(
                "This file's text came through looking garbled -- possibly "
                "a scanned PDF without OCR. Try re-uploading a text-based "
                "version if you have one."
            ),
        )

    return ConfidenceResult(level="high", message=None)
