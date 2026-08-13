from .. import models, schemas
from ..crud_factory import make_year_crud_router

router = make_year_crud_router(
    model=models.Spray,
    create_schema=schemas.SprayCreate,
    update_schema=schemas.SprayUpdate,
    out_schema=schemas.SprayOut,
    prefix="/sprays",
    tags=["sprays"],
    field_filter=True,
)
