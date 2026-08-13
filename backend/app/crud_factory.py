from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from .database import get_db
from .farm import get_current_farm_id


def _get_owned_or_404(db: Session, model, item_id: int, farm_id: int):
    item = db.get(model, item_id)
    if item is None or item.farm_id != farm_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    return item


def make_simple_crud_router(
    *,
    model,
    create_schema,
    update_schema,
    out_schema,
    prefix: str,
    tags: list[str],
    nullify_on_delete: list[tuple] | None = None,
):
    """CRUD with no query filters — used for fields and machines.

    nullify_on_delete: list of (child_model, fk_column_name) pairs whose matching rows
    get their FK set to NULL instead of being cascade-deleted, per spec.
    """
    router = APIRouter(prefix=prefix, tags=tags)

    @router.get("", response_model=list[out_schema])
    def list_items(farm_id: int = Depends(get_current_farm_id), db: Session = Depends(get_db)):
        return db.query(model).filter(model.farm_id == farm_id).order_by(model.name).all()

    @router.post("", response_model=out_schema, status_code=status.HTTP_201_CREATED)
    def create_item(
        payload: create_schema, farm_id: int = Depends(get_current_farm_id), db: Session = Depends(get_db)
    ):
        item = model(**payload.model_dump(), farm_id=farm_id)
        db.add(item)
        db.commit()
        db.refresh(item)
        return item

    @router.put("/{item_id}", response_model=out_schema)
    def update_item(
        item_id: int,
        payload: update_schema,
        farm_id: int = Depends(get_current_farm_id),
        db: Session = Depends(get_db),
    ):
        item = _get_owned_or_404(db, model, item_id, farm_id)
        for key, value in payload.model_dump(exclude_unset=True).items():
            setattr(item, key, value)
        db.commit()
        db.refresh(item)
        return item

    @router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
    def delete_item(item_id: int, farm_id: int = Depends(get_current_farm_id), db: Session = Depends(get_db)):
        item = _get_owned_or_404(db, model, item_id, farm_id)
        if nullify_on_delete:
            for child_model, fk_name in nullify_on_delete:
                (
                    db.query(child_model)
                    .filter(getattr(child_model, fk_name) == item_id, child_model.farm_id == farm_id)
                    .update({fk_name: None})
                )
        db.delete(item)
        db.commit()
        return None

    return router


def make_year_crud_router(
    *,
    model,
    create_schema,
    update_schema,
    out_schema,
    prefix: str,
    tags: list[str],
    field_filter: bool = False,
):
    """CRUD filterable by year (and optionally field_id) — used for crops, inputs, sprays,
    maintenance, and the weather event tables."""
    router = APIRouter(prefix=prefix, tags=tags)

    @router.get("", response_model=list[out_schema])
    def list_items(
        year: Optional[int] = Query(None),
        field_id: Optional[int] = Query(None),
        farm_id: int = Depends(get_current_farm_id),
        db: Session = Depends(get_db),
    ):
        query = db.query(model).filter(model.farm_id == farm_id)
        if year is not None:
            query = query.filter(model.year == year)
        if field_filter and field_id is not None:
            query = query.filter(model.field_id == field_id)
        return query.order_by(model.year.desc(), model.id.desc()).all()

    @router.post("", response_model=out_schema, status_code=status.HTTP_201_CREATED)
    def create_item(
        payload: create_schema, farm_id: int = Depends(get_current_farm_id), db: Session = Depends(get_db)
    ):
        item = model(**payload.model_dump(), farm_id=farm_id)
        db.add(item)
        db.commit()
        db.refresh(item)
        return item

    @router.put("/{item_id}", response_model=out_schema)
    def update_item(
        item_id: int,
        payload: update_schema,
        farm_id: int = Depends(get_current_farm_id),
        db: Session = Depends(get_db),
    ):
        item = _get_owned_or_404(db, model, item_id, farm_id)
        for key, value in payload.model_dump(exclude_unset=True).items():
            setattr(item, key, value)
        db.commit()
        db.refresh(item)
        return item

    @router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
    def delete_item(item_id: int, farm_id: int = Depends(get_current_farm_id), db: Session = Depends(get_db)):
        item = _get_owned_or_404(db, model, item_id, farm_id)
        db.delete(item)
        db.commit()
        return None

    return router
