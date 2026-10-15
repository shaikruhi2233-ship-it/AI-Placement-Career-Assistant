from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app import db_models, schemas
from app.database import get_db
from app.services import chatbot

router = APIRouter(prefix="/chatbot", tags=["AI Career Chatbot"])


@router.post("/message", response_model=schemas.ChatResponseOut)
def send_message(payload: schemas.ChatRequest, db: Session = Depends(get_db)):
    # student_id + db must be passed through so the chatbot can answer with
    # the student's REAL numbers (skill gap %, ATS score, readiness score,
    # top job matches, ...) instead of only the canned navigation reply.
    result = chatbot.get_reply(payload.message, student_id=payload.student_id, db=db)

    if payload.student_id:
        db.add(db_models.ChatMessage(
            student_id=payload.student_id, role="user", message=payload.message, intent=result["intent"]
        ))
        db.add(db_models.ChatMessage(
            student_id=payload.student_id, role="bot", message=result["reply"], intent=result["intent"]
        ))
        db.commit()

    return result


@router.get("/history/{student_id}", response_model=List[schemas.ChatHistoryItem])
def get_history(student_id: int, db: Session = Depends(get_db)):
    return (
        db.query(db_models.ChatMessage)
        .filter(db_models.ChatMessage.student_id == student_id)
        .order_by(db_models.ChatMessage.created_at.asc())
        .all()
    )
