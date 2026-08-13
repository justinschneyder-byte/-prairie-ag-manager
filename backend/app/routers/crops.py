from .. import models, schemas
from ..crud_factory import make_year_crud_router

router = make_year_crud_router(
    model=models.Crop,
    create_schema=schemas.CropCreate,
    update_schema=schemas.CropUpdate,
    out_schema=schemas.CropOut,
    prefix="/crops",
    tags=["crops"],
    field_filter=True,
)
