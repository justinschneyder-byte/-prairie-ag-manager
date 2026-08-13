from datetime import date, datetime
from decimal import Decimal

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .. import models
from ..database import get_db
from ..farm import get_current_farm_id

router = APIRouter(tags=["data"])

EXPORT_TABLES = {
    "fields": models.Field,
    "machines": models.Machine,
    "crops": models.Crop,
    "inputs": models.Input,
    "sprays": models.Spray,
    "maintenance": models.Maintenance,
    "rain_events": models.RainEvent,
    "frost_events": models.FrostEvent,
    "hail_events": models.HailEvent,
}

# Columns that are server-managed and should not be copied back in on import.
SKIP_COLUMNS = {"id", "farm_id", "created_at", "updated_at"}


def _jsonable(value):
    if isinstance(value, Decimal):
        return float(value)
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    return value


def _row_to_dict(row) -> dict:
    return {c.name: _jsonable(getattr(row, c.name)) for c in row.__table__.columns}


@router.get("/export")
def export_data(farm_id: int = Depends(get_current_farm_id), db: Session = Depends(get_db)):
    dump = {"exported_at": datetime.utcnow().isoformat(), "farm_id": farm_id}
    for key, model in EXPORT_TABLES.items():
        rows = db.query(model).filter(model.farm_id == farm_id).all()
        dump[key] = [_row_to_dict(r) for r in rows]
    return dump


@router.post("/import")
def import_data(payload: dict, farm_id: int = Depends(get_current_farm_id), db: Session = Depends(get_db)):
    """Restore records from a JSON dump produced by GET /export.

    Inserts rows as NEW records scoped to the current farm (original ids are not reused,
    to avoid colliding with existing data). Safe to run multiple times; it will duplicate
    rows if run twice with the same file, so only import a given backup once.
    """
    counts = {}
    for key, model in EXPORT_TABLES.items():
        rows = payload.get(key) or []
        inserted = 0
        for row in rows:
            clean = {k: v for k, v in row.items() if k not in SKIP_COLUMNS}
            db.add(model(**clean, farm_id=farm_id))
            inserted += 1
        counts[key] = inserted
    db.commit()
    return {"imported": counts}
