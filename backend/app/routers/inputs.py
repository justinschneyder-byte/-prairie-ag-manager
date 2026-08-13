from .. import models, schemas
from ..crud_factory import make_year_crud_router

router = make_year_crud_router(
    model=models.Input,
    create_schema=schemas.InputCreate,
    update_schema=schemas.InputUpdate,
    out_schema=schemas.InputOut,
    prefix="/inputs",
    tags=["inputs"],
    field_filter=True,
)
