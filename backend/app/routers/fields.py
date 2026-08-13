from .. import models, schemas
from ..crud_factory import make_simple_crud_router

router = make_simple_crud_router(
    model=models.Field,
    create_schema=schemas.FieldCreate,
    update_schema=schemas.FieldUpdate,
    out_schema=schemas.FieldOut,
    prefix="/fields",
    tags=["fields"],
    nullify_on_delete=[
        (models.Crop, "field_id"),
        (models.Input, "field_id"),
        (models.Spray, "field_id"),
    ],
)
