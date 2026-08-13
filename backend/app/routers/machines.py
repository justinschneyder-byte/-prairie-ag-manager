from .. import models, schemas
from ..crud_factory import make_simple_crud_router

router = make_simple_crud_router(
    model=models.Machine,
    create_schema=schemas.MachineCreate,
    update_schema=schemas.MachineUpdate,
    out_schema=schemas.MachineOut,
    prefix="/machines",
    tags=["machines"],
    nullify_on_delete=[
        (models.Maintenance, "machine_id"),
    ],
)
