from decimal import Decimal

from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from .. import models, schemas
from ..crud_factory import make_simple_crud_router
from ..database import get_db
from ..farm import get_current_farm_id

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


@router.get("/{field_id}/history", response_model=schemas.FieldHistory)
def field_history(
    field_id: int,
    farm_id: int = Depends(get_current_farm_id),
    db: Session = Depends(get_db),
):
    field = db.get(models.Field, field_id)
    if field is None or field.farm_id != farm_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")

    crops = db.query(models.Crop).filter(models.Crop.field_id == field_id, models.Crop.farm_id == farm_id).all()
    inputs = db.query(models.Input).filter(models.Input.field_id == field_id, models.Input.farm_id == farm_id).all()
    sprays = db.query(models.Spray).filter(models.Spray.field_id == field_id, models.Spray.farm_id == farm_id).all()

    years = sorted({r.year for r in [*crops, *inputs, *sprays]}, reverse=True)

    result_years = []
    for year in years:
        year_inputs = [i for i in inputs if i.year == year]
        result_years.append(
            {
                "year": year,
                "crops": [c for c in crops if c.year == year],
                "inputs": year_inputs,
                "sprays": [s for s in sprays if s.year == year],
                "total_cost": sum((i.cost or Decimal(0)) for i in year_inputs),
            }
        )

    return {"field": field, "years": result_years}
