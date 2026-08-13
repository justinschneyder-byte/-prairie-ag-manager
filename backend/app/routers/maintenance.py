from .. import models, schemas
from ..crud_factory import make_year_crud_router

router = make_year_crud_router(
    model=models.Maintenance,
    create_schema=schemas.MaintenanceCreate,
    update_schema=schemas.MaintenanceUpdate,
    out_schema=schemas.MaintenanceOut,
    prefix="/maintenance",
    tags=["maintenance"],
)
