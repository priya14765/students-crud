from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .. import ai, schemas
from ..database import get_db

router = APIRouter(tags=["AI (optional)"])


@router.post("/ask", response_model=schemas.AskResponse)
def ask(payload: schemas.AskRequest, db: Session = Depends(get_db)):
    records, total = ai.select_records(db, payload.question)
    context = ai.build_context(records, total)
    try:
        answer = ai.ask_ollama(payload.question, context)
    except ai.OllamaUnavailable:
        raise HTTPException(
            status.HTTP_503_SERVICE_UNAVAILABLE,
            f"Ollama is not reachable. Start it and run: ollama pull {ai.OLLAMA_MODEL}",
        )
    return schemas.AskResponse(
        question=payload.question,
        answer=answer,
        model=ai.OLLAMA_MODEL,
        records_used=[s.id for s in records[: ai.MAX_RECORDS]],
    )
