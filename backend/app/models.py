from sqlalchemy import (
    Column,
    Integer,
    Numeric,
    Text,
    ForeignKey,
    DateTime,
    Index,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import relationship

from .database import Base


class Farm(Base):
    __tablename__ = "farms"

    id = Column(Integer, primary_key=True)
    name = Column(Text, nullable=False, default="Prairie Ag Manager")
    location = Column(Text, default="Magrath, Alberta")
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    farm_id = Column(Integer, ForeignKey("farms.id"), index=True)
    name = Column(Text, nullable=False)
    email = Column(Text, unique=True)
    password_hash = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (UniqueConstraint("farm_id", "name", name="uq_users_farm_name"),)


class Field(Base):
    __tablename__ = "fields"

    id = Column(Integer, primary_key=True)
    farm_id = Column(Integer, ForeignKey("farms.id"), index=True)
    name = Column(Text, nullable=False)
    acres = Column(Numeric)
    soil_type = Column(Text)
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class Machine(Base):
    __tablename__ = "machines"

    id = Column(Integer, primary_key=True)
    farm_id = Column(Integer, ForeignKey("farms.id"), index=True)
    name = Column(Text, nullable=False)
    model_year = Column(Integer)
    serial_number = Column(Text)
    hours = Column(Numeric)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class Crop(Base):
    __tablename__ = "crops"

    id = Column(Integer, primary_key=True)
    farm_id = Column(Integer, ForeignKey("farms.id"), index=True)
    field_id = Column(Integer, ForeignKey("fields.id"), index=True)
    year = Column(Integer, nullable=False)
    crop = Column(Text)
    variety = Column(Text)
    seeded_date = Column(Text)
    harvested_date = Column(Text)
    bushels_per_acre = Column(Numeric)
    total_bushels = Column(Numeric)
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    __table_args__ = (Index("ix_crops_farm_year", "farm_id", "year"),)


class Input(Base):
    __tablename__ = "inputs"

    id = Column(Integer, primary_key=True)
    farm_id = Column(Integer, ForeignKey("farms.id"), index=True)
    field_id = Column(Integer, ForeignKey("fields.id"), index=True)
    year = Column(Integer, nullable=False)
    date = Column(Text)
    type = Column(Text)
    product = Column(Text)
    rate_per_acre = Column(Text)
    total_amount = Column(Text)
    cost = Column(Numeric)
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    __table_args__ = (Index("ix_inputs_farm_year", "farm_id", "year"),)


class Spray(Base):
    __tablename__ = "sprays"

    id = Column(Integer, primary_key=True)
    farm_id = Column(Integer, ForeignKey("farms.id"), index=True)
    field_id = Column(Integer, ForeignKey("fields.id"), index=True)
    year = Column(Integer, nullable=False)
    date = Column(Text)
    crop = Column(Text)
    products = Column(Text)
    acres = Column(Numeric)
    wind = Column(Text)
    temp = Column(Text)
    operator = Column(Text)
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    __table_args__ = (Index("ix_sprays_farm_year", "farm_id", "year"),)


class Maintenance(Base):
    __tablename__ = "maintenance"

    id = Column(Integer, primary_key=True)
    farm_id = Column(Integer, ForeignKey("farms.id"), index=True)
    machine_id = Column(Integer, ForeignKey("machines.id"), index=True)
    year = Column(Integer, nullable=False)
    date = Column(Text)
    type = Column(Text)
    description = Column(Text)
    parts = Column(Text)
    cost = Column(Numeric)
    done_by = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    __table_args__ = (Index("ix_maintenance_farm_year", "farm_id", "year"),)


class RainEvent(Base):
    __tablename__ = "rain_events"

    id = Column(Integer, primary_key=True)
    farm_id = Column(Integer, ForeignKey("farms.id"), index=True)
    year = Column(Integer, nullable=False)
    date = Column(Text)
    month = Column(Integer)
    mm = Column(Numeric)
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (Index("ix_rain_events_farm_year", "farm_id", "year"),)


class FrostEvent(Base):
    __tablename__ = "frost_events"

    id = Column(Integer, primary_key=True)
    farm_id = Column(Integer, ForeignKey("farms.id"), index=True)
    year = Column(Integer, nullable=False)
    date = Column(Text)
    type = Column(Text)
    temp_c = Column(Numeric)
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (Index("ix_frost_events_farm_year", "farm_id", "year"),)


class HailEvent(Base):
    __tablename__ = "hail_events"

    id = Column(Integer, primary_key=True)
    farm_id = Column(Integer, ForeignKey("farms.id"), index=True)
    year = Column(Integer, nullable=False)
    date = Column(Text)
    severity = Column(Text)
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (Index("ix_hail_events_farm_year", "farm_id", "year"),)


class ChatLog(Base):
    __tablename__ = "chat_log"

    id = Column(Integer, primary_key=True)
    farm_id = Column(Integer, ForeignKey("farms.id"), index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    role = Column(Text)
    content = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
