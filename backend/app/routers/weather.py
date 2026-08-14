from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from .. import models, schemas
from .. import open_meteo
from ..crud_factory import make_year_crud_router
from ..database import get_db

rain_router = make_year_crud_router(
    model=models.RainEvent,
    create_schema=schemas.RainCreate,
    update_schema=schemas.RainUpdate,
    out_schema=schemas.RainOut,
    prefix="/weather/rain",
    tags=["weather"],
)

frost_router = make_year_crud_router(
    model=models.FrostEvent,
    create_schema=schemas.FrostCreate,
    update_schema=schemas.FrostUpdate,
    out_schema=schemas.FrostOut,
    prefix="/weather/frost",
    tags=["weather"],
)

hail_router = make_year_crud_router(
    model=models.HailEvent,
    create_schema=schemas.HailCreate,
    update_schema=schemas.HailUpdate,
    out_schema=schemas.HailOut,
    prefix="/weather/hail",
    tags=["weather"],
)

regional_router = APIRouter(prefix="/weather", tags=["weather"])


@regional_router.get("/regional-history")
def regional_history(year: int = Query(...), db: Session = Depends(get_db)):
    try:
        return open_meteo.get_regional_history(db, year)
    except RuntimeError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc))


@regional_router.get("/regional-forecast")
def regional_forecast(db: Session = Depends(get_db)):
    try:
        return open_meteo.get_regional_forecast(db)
    except RuntimeError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc))


routers = [rain_router, frost_router, hail_router, regional_router]
