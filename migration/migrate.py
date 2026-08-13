r"""
One-off migration: load the Claude.ai prototype's exported backup JSON and insert it into the
new Postgres schema, remapping the old short field names to the new columns.

Usage:
    cd migration
    ..\backend\.venv\Scripts\python.exe migrate.py path\to\backup.json

Reads DATABASE_URL the same way the backend does (backend/.env, or the DATABASE_URL env var).
Run this against the real Railway Postgres DATABASE_URL when you're ready to migrate for real —
point backend/.env at it first, or export DATABASE_URL before running.

Old backup shape (from the prototype's Backup button):
{
  "fields": [{"id", "name", "acres", "soil", "notes"}],
  "machines": [{"id", "name", "yr", "sn", "hrs"}],
  "crops": [{"id", "fid", "yr", "crop", "variety", "seed", "harv", "bpa", "tot", "notes"}],
  "inputs": [{"id", "fid", "yr", "date", "type", "prod", "rate", "tot", "cost", "notes"}],
  "sprays": [{"id", "fid", "yr", "date", "crop", "prods", "ac", "wind", "temp", "op", "notes"}],
  "maint": [{"id", "mid", "yr", "date", "type", "desc", "parts", "cost", "by"}],
  "weather": { "<year>": { "rain": [...], "frost": [...], "hail": [...] } }
}

field_id / machine_id references (fid, mid) are remapped from the old ids to the newly
inserted rows' ids — the old ids are not reused, since they're just SERIAL positions in a
key-value store, not guaranteed unique across a real Postgres install.
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend"))

from app import models  # noqa: E402
from app.database import SessionLocal, Base, engine  # noqa: E402


def g(d: dict, *keys, default=None):
    """First present key from a dict, trying each candidate name in order."""
    for k in keys:
        if k in d and d[k] not in (None, ""):
            return d[k]
    return default


def migrate(backup_path: str):
    data = json.loads(Path(backup_path).read_text(encoding="utf-8"))

    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        farm = db.query(models.Farm).first()
        if farm is None:
            farm = models.Farm()
            db.add(farm)
            db.commit()
            db.refresh(farm)
        farm_id = farm.id

        field_id_map = {}
        for row in data.get("fields", []):
            field = models.Field(
                farm_id=farm_id,
                name=g(row, "name"),
                acres=g(row, "acres"),
                soil_type=g(row, "soil", "soil_type"),
                notes=g(row, "notes"),
            )
            db.add(field)
            db.commit()
            db.refresh(field)
            field_id_map[row.get("id")] = field.id
        print(f"Migrated {len(field_id_map)} fields")

        machine_id_map = {}
        for row in data.get("machines", []):
            machine = models.Machine(
                farm_id=farm_id,
                name=g(row, "name"),
                model_year=g(row, "yr", "model_year"),
                serial_number=g(row, "sn", "serial_number"),
                hours=g(row, "hrs", "hours"),
            )
            db.add(machine)
            db.commit()
            db.refresh(machine)
            machine_id_map[row.get("id")] = machine.id
        print(f"Migrated {len(machine_id_map)} machines")

        crop_count = 0
        for row in data.get("crops", []):
            db.add(
                models.Crop(
                    farm_id=farm_id,
                    field_id=field_id_map.get(g(row, "fid", "field_id")),
                    year=g(row, "yr", "year"),
                    crop=g(row, "crop"),
                    variety=g(row, "variety"),
                    seeded_date=g(row, "seed", "seeded_date"),
                    harvested_date=g(row, "harv", "harvested_date"),
                    bushels_per_acre=g(row, "bpa", "bushels_per_acre"),
                    total_bushels=g(row, "tot", "total_bushels"),
                    notes=g(row, "notes"),
                )
            )
            crop_count += 1
        db.commit()
        print(f"Migrated {crop_count} crop records")

        input_count = 0
        for row in data.get("inputs", []):
            db.add(
                models.Input(
                    farm_id=farm_id,
                    field_id=field_id_map.get(g(row, "fid", "field_id")),
                    year=g(row, "yr", "year"),
                    date=g(row, "date"),
                    type=g(row, "type"),
                    product=g(row, "prod", "product"),
                    rate_per_acre=g(row, "rate", "rate_per_acre"),
                    total_amount=g(row, "tot", "total_amount"),
                    cost=g(row, "cost"),
                    notes=g(row, "notes"),
                )
            )
            input_count += 1
        db.commit()
        print(f"Migrated {input_count} input records")

        spray_count = 0
        for row in data.get("sprays", []):
            db.add(
                models.Spray(
                    farm_id=farm_id,
                    field_id=field_id_map.get(g(row, "fid", "field_id")),
                    year=g(row, "yr", "year"),
                    date=g(row, "date"),
                    crop=g(row, "crop"),
                    products=g(row, "prods", "products"),
                    acres=g(row, "ac", "acres"),
                    wind=g(row, "wind"),
                    temp=g(row, "temp"),
                    operator=g(row, "op", "operator"),
                    notes=g(row, "notes"),
                )
            )
            spray_count += 1
        db.commit()
        print(f"Migrated {spray_count} spray records")

        maint_count = 0
        for row in data.get("maint", []):
            db.add(
                models.Maintenance(
                    farm_id=farm_id,
                    machine_id=machine_id_map.get(g(row, "mid", "machine_id")),
                    year=g(row, "yr", "year"),
                    date=g(row, "date"),
                    type=g(row, "type"),
                    description=g(row, "desc", "description"),
                    parts=g(row, "parts"),
                    cost=g(row, "cost"),
                    done_by=g(row, "by", "done_by"),
                )
            )
            maint_count += 1
        db.commit()
        print(f"Migrated {maint_count} maintenance records")

        rain_count = frost_count = hail_count = 0
        weather = data.get("weather", {})
        for year_str, buckets in weather.items():
            try:
                year = int(year_str)
            except (TypeError, ValueError):
                continue

            for row in buckets.get("rain", []):
                db.add(
                    models.RainEvent(
                        farm_id=farm_id,
                        year=year,
                        date=g(row, "d", "date"),
                        month=g(row, "m", "month"),
                        mm=g(row, "mm"),
                        notes=g(row, "n", "notes"),
                    )
                )
                rain_count += 1

            for row in buckets.get("frost", []):
                db.add(
                    models.FrostEvent(
                        farm_id=farm_id,
                        year=year,
                        date=g(row, "d", "date"),
                        type=g(row, "t", "type"),
                        temp_c=g(row, "c", "temp", "temp_c"),
                        notes=g(row, "n", "notes"),
                    )
                )
                frost_count += 1

            for row in buckets.get("hail", []):
                db.add(
                    models.HailEvent(
                        farm_id=farm_id,
                        year=year,
                        date=g(row, "d", "date"),
                        severity=g(row, "sev", "severity"),
                        notes=g(row, "n", "notes"),
                    )
                )
                hail_count += 1

        db.commit()
        print(f"Migrated {rain_count} rain / {frost_count} frost / {hail_count} hail events")

        print("Migration complete.")
    finally:
        db.close()


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python migrate.py path/to/backup.json")
        sys.exit(1)
    migrate(sys.argv[1])
