from fastapi import Depends
from sqlalchemy.orm import Session

from . import models
from .database import get_db


def get_current_farm_id(db: Session = Depends(get_db)) -> int:
    """Single-tenant app, no auth — resolve the one farm row (creating it if missing)."""
    farm = db.query(models.Farm).first()
    if farm is None:
        farm = models.Farm()
        db.add(farm)
        db.commit()
        db.refresh(farm)
    return farm.id
