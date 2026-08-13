from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict


class ORMBase(BaseModel):
    model_config = ConfigDict(from_attributes=True, protected_namespaces=())


# ---------- Fields ----------


class FieldBase(BaseModel):
    name: str
    acres: Optional[Decimal] = None
    soil_type: Optional[str] = None
    notes: Optional[str] = None


class FieldCreate(FieldBase):
    pass


class FieldUpdate(BaseModel):
    name: Optional[str] = None
    acres: Optional[Decimal] = None
    soil_type: Optional[str] = None
    notes: Optional[str] = None


class FieldOut(FieldBase, ORMBase):
    id: int
    farm_id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


# ---------- Machines ----------


class MachineBase(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    name: str
    model_year: Optional[int] = None
    serial_number: Optional[str] = None
    hours: Optional[Decimal] = None


class MachineCreate(MachineBase):
    pass


class MachineUpdate(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    name: Optional[str] = None
    model_year: Optional[int] = None
    serial_number: Optional[str] = None
    hours: Optional[Decimal] = None


class MachineOut(MachineBase, ORMBase):
    id: int
    farm_id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


# ---------- Crops ----------


class CropBase(BaseModel):
    field_id: Optional[int] = None
    year: int
    crop: Optional[str] = None
    variety: Optional[str] = None
    seeded_date: Optional[str] = None
    harvested_date: Optional[str] = None
    bushels_per_acre: Optional[Decimal] = None
    total_bushels: Optional[Decimal] = None
    notes: Optional[str] = None


class CropCreate(CropBase):
    pass


class CropUpdate(BaseModel):
    field_id: Optional[int] = None
    year: Optional[int] = None
    crop: Optional[str] = None
    variety: Optional[str] = None
    seeded_date: Optional[str] = None
    harvested_date: Optional[str] = None
    bushels_per_acre: Optional[Decimal] = None
    total_bushels: Optional[Decimal] = None
    notes: Optional[str] = None


class CropOut(CropBase, ORMBase):
    id: int
    farm_id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


# ---------- Inputs ----------


class InputBase(BaseModel):
    field_id: Optional[int] = None
    year: int
    date: Optional[str] = None
    type: Optional[str] = None
    product: Optional[str] = None
    rate_per_acre: Optional[str] = None
    total_amount: Optional[str] = None
    cost: Optional[Decimal] = None
    notes: Optional[str] = None


class InputCreate(InputBase):
    pass


class InputUpdate(BaseModel):
    field_id: Optional[int] = None
    year: Optional[int] = None
    date: Optional[str] = None
    type: Optional[str] = None
    product: Optional[str] = None
    rate_per_acre: Optional[str] = None
    total_amount: Optional[str] = None
    cost: Optional[Decimal] = None
    notes: Optional[str] = None


class InputOut(InputBase, ORMBase):
    id: int
    farm_id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


# ---------- Sprays ----------


class SprayBase(BaseModel):
    field_id: Optional[int] = None
    year: int
    date: Optional[str] = None
    crop: Optional[str] = None
    products: Optional[str] = None
    acres: Optional[Decimal] = None
    wind: Optional[str] = None
    temp: Optional[str] = None
    operator: Optional[str] = None
    notes: Optional[str] = None


class SprayCreate(SprayBase):
    pass


class SprayUpdate(BaseModel):
    field_id: Optional[int] = None
    year: Optional[int] = None
    date: Optional[str] = None
    crop: Optional[str] = None
    products: Optional[str] = None
    acres: Optional[Decimal] = None
    wind: Optional[str] = None
    temp: Optional[str] = None
    operator: Optional[str] = None
    notes: Optional[str] = None


class SprayOut(SprayBase, ORMBase):
    id: int
    farm_id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


# ---------- Maintenance ----------


class MaintenanceBase(BaseModel):
    machine_id: Optional[int] = None
    year: int
    date: Optional[str] = None
    type: Optional[str] = None
    description: Optional[str] = None
    parts: Optional[str] = None
    cost: Optional[Decimal] = None
    done_by: Optional[str] = None


class MaintenanceCreate(MaintenanceBase):
    pass


class MaintenanceUpdate(BaseModel):
    machine_id: Optional[int] = None
    year: Optional[int] = None
    date: Optional[str] = None
    type: Optional[str] = None
    description: Optional[str] = None
    parts: Optional[str] = None
    cost: Optional[Decimal] = None
    done_by: Optional[str] = None


class MaintenanceOut(MaintenanceBase, ORMBase):
    id: int
    farm_id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


# ---------- Weather: Rain ----------


class RainBase(BaseModel):
    year: int
    date: Optional[str] = None
    month: Optional[int] = None
    mm: Optional[Decimal] = None
    notes: Optional[str] = None


class RainCreate(RainBase):
    pass


class RainUpdate(BaseModel):
    year: Optional[int] = None
    date: Optional[str] = None
    month: Optional[int] = None
    mm: Optional[Decimal] = None
    notes: Optional[str] = None


class RainOut(RainBase, ORMBase):
    id: int
    farm_id: Optional[int] = None
    created_at: Optional[datetime] = None


# ---------- Weather: Frost ----------


class FrostBase(BaseModel):
    year: int
    date: Optional[str] = None
    type: Optional[str] = None
    temp_c: Optional[Decimal] = None
    notes: Optional[str] = None


class FrostCreate(FrostBase):
    pass


class FrostUpdate(BaseModel):
    year: Optional[int] = None
    date: Optional[str] = None
    type: Optional[str] = None
    temp_c: Optional[Decimal] = None
    notes: Optional[str] = None


class FrostOut(FrostBase, ORMBase):
    id: int
    farm_id: Optional[int] = None
    created_at: Optional[datetime] = None


# ---------- Weather: Hail ----------


class HailBase(BaseModel):
    year: int
    date: Optional[str] = None
    severity: Optional[str] = None
    notes: Optional[str] = None


class HailCreate(HailBase):
    pass


class HailUpdate(BaseModel):
    year: Optional[int] = None
    date: Optional[str] = None
    severity: Optional[str] = None
    notes: Optional[str] = None


class HailOut(HailBase, ORMBase):
    id: int
    farm_id: Optional[int] = None
    created_at: Optional[datetime] = None


# ---------- Chat ----------


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    message: str
    action: str
    record: Optional[dict] = None
