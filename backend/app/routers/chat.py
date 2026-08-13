from datetime import date, datetime
from decimal import Decimal

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .. import models, schemas
from ..chat_logic import apply_record, parse_message
from ..database import get_db
from ..farm import get_current_farm_id

router = APIRouter(prefix="/chat", tags=["chat"])


def _jsonable(value):
    if isinstance(value, Decimal):
        return float(value)
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    return value


@router.post("", response_model=schemas.ChatResponse)
def chat(
    payload: schemas.ChatRequest,
    farm_id: int = Depends(get_current_farm_id),
    db: Session = Depends(get_db),
):
    db.add(models.ChatLog(farm_id=farm_id, role="user", content=payload.message))
    db.commit()

    result = parse_message(db, farm_id, payload.message)
    created = apply_record(db, farm_id, result["action"], result["record"])

    record_out = None
    if created is not None:
        record_out = {c.name: _jsonable(getattr(created, c.name)) for c in created.__table__.columns}

    db.add(models.ChatLog(farm_id=farm_id, role="assistant", content=result["message"]))
    db.commit()

    return schemas.ChatResponse(message=result["message"], action=result["action"], record=record_out)
