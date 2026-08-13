from .. import models, schemas
from ..crud_factory import make_year_crud_router

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

routers = [rain_router, frost_router, hail_router]
