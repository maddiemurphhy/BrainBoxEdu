"""
Wraps the Anthropic API call for question generation.

The whole point of this file, given the project's risk list, is that
the model is NOT allowed to freely invent questions from its own
knowledge. It's instructed to work only from the text we hand it, and
to attach a short verbatim-ish excerpt to every question so the
student can check it against the source. If a question can't come
with a real excerpt, we throw it out in code (not just by asking the
model nicely) -- see _filter_ungrounded below.
"""
import json
import os

from anthropic import Anthropic

from app.config import settings

# You can override this in .env without touching code. Check
# https://docs.claude.com for the current recommended model name if
# this one becomes outdated.
MODEL_NAME = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-5")

SYSTEM_PROMPT = """You are a study-question generator. You will be given a block \
of text extracted from a student's lecture notes or slides. Generate study \
questions STRICTLY from that text.

Rules you must follow:
1. Every question must be answerable using only the provided text -- never use \
outside knowledge to write a question or its answer.
2. Every question must include a "source_excerpt": a short quote (1-2 \
sentences, copied as closely as possible from the provided text) that the \
question is based on. If you cannot find a real excerpt to support a \
question, do not include that question at all.
3. Return ONLY valid JSON: a list of objects with keys "question", "answer", \
and "source_excerpt". No prose before or after the JSON, no markdown code \
fences.
"""


def generate_questions(material_text: str, num_questions: int = 5) -> list[dict]:
    client = Anthropic(api_key=settings.anthropic_api_key)

    user_prompt = (
        f"Generate up to {num_questions} study questions from the text below.\n\n"
        f"--- BEGIN MATERIAL ---\n{material_text}\n--- END MATERIAL ---"
    )

    response = client.messages.create(
        model=MODEL_NAME,
        max_tokens=2000,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_prompt}],
    )

    raw_text = response.content[0].text
    questions = _parse_json_questions(raw_text)
    return _filter_ungrounded(questions, material_text)


def _parse_json_questions(raw_text: str) -> list[dict]:
    try:
        data = json.loads(raw_text)
        if isinstance(data, list):
            return data
        return []
    except json.JSONDecodeError:
        # The model occasionally wraps JSON in text/fences despite instructions.
        # Try to pull out the first [...] block as a fallback.
        start = raw_text.find("[")
        end = raw_text.rfind("]")
        if start != -1 and end != -1:
            try:
                return json.loads(raw_text[start : end + 1])
            except json.JSONDecodeError:
                return []
        return []


def _filter_ungrounded(questions: list[dict], material_text: str) -> list[dict]:
    """
    Belt-and-suspenders check: drop any question missing the required
    fields, or whose source_excerpt doesn't actually appear (loosely)
    in the original material. This is what makes rule #2 above a real
    guarantee instead of just a polite request to the model.
    """
    normalized_material = _normalize(material_text)
    kept = []
    for q in questions:
        if not all(k in q and q[k] for k in ("question", "answer", "source_excerpt")):
            continue
        if _normalize(q["source_excerpt"])[:40] in normalized_material:
            kept.append(q)
    return kept


def _normalize(text: str) -> str:
    return " ".join(text.lower().split())
