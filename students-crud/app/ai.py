"""Optional bonus: answer natural-language questions with a local Ollama model.

Safety design: the model NEVER writes or runs SQL. Backend code decides which
records are relevant (simple keyword/year rules), fetches them with normal ORM
queries, and passes them to the model as read-only context.
"""
import os
import re
from datetime import date

import httpx
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from . import models

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2:1b")
MAX_RECORDS = 50

SYSTEM_PROMPT = (
    "You answer questions about a student database. Use ONLY the data provided "
    "in the context. The numbers labelled TOTAL and MATCHING are exact - never "
    "recalculate them. If the answer is not in the context, say you don't know. "
    "Be short and clear."
)


class OllamaUnavailable(Exception):
    pass


def select_records(db: Session, question: str) -> tuple[list[models.Student], int]:
    """Pick relevant records using fixed rules. Returns (records, total_students)."""
    q = question.lower()
    total = db.scalar(select(func.count()).select_from(models.Student)) or 0
    stmt = select(models.Student)

    year_match = re.search(r"\b(19|20)\d{2}\b", q)
    if year_match:
        year = int(year_match.group())
        if "after" in q or "later than" in q:
            stmt = stmt.where(models.Student.date_of_birth >= date(year + 1, 1, 1))
        elif "before" in q or "earlier than" in q:
            stmt = stmt.where(models.Student.date_of_birth < date(year, 1, 1))
        elif "born" in q or "in " in q:
            stmt = stmt.where(
                models.Student.date_of_birth >= date(year, 1, 1),
                models.Student.date_of_birth < date(year + 1, 1, 1),
            )

    courses = [c for c in db.scalars(select(models.Student.course).distinct()) if c]
    for course in courses:
        if course.lower() in q:
            stmt = stmt.where(models.Student.course == course)
            break

    records = list(db.scalars(stmt.order_by(models.Student.id)))
    return records, total


def build_context(records: list[models.Student], total: int) -> str:
    lines = [f"TOTAL students in database: {total}", f"MATCHING records shown: {len(records)}"]
    for s in records[:MAX_RECORDS]:
        lines.append(
            f"- id={s.id}; name={s.name}; dob={s.date_of_birth}; email={s.email}; "
            f"phone={s.phone}; course={s.course}; enrolled={s.enrollment_date}"
        )
    if len(records) > MAX_RECORDS:
        lines.append(f"(list truncated to first {MAX_RECORDS} records)")
    return "\n".join(lines)


def ask_ollama(question: str, context: str) -> str:
    payload = {
        "model": OLLAMA_MODEL,
        "stream": False,
        "options": {"temperature": 0},
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"CONTEXT:\n{context}\n\nQUESTION: {question}"},
        ],
    }
    try:
        resp = httpx.post(f"{OLLAMA_URL}/api/chat", json=payload, timeout=120)
        resp.raise_for_status()
        return resp.json()["message"]["content"].strip()
    except (httpx.HTTPError, KeyError, ValueError) as exc:
        raise OllamaUnavailable(str(exc)) from exc
