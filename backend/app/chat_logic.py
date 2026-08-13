import json
from datetime import date

from anthropic import Anthropic
from sqlalchemy.orm import Session

from . import models
from .config import get_settings

settings = get_settings()

VALID_ACTIONS = {"field", "machine", "rain", "frost", "hail", "crop", "spray", "input", "maint", "none"}

ACTION_TO_MODEL = {
    "field": models.Field,
    "machine": models.Machine,
    "rain": models.RainEvent,
    "frost": models.FrostEvent,
    "hail": models.HailEvent,
    "crop": models.Crop,
    "spray": models.Spray,
    "input": models.Input,
    "maint": models.Maintenance,
}

# Fields on each model a record dict is allowed to set (besides farm_id, which is always injected).
ACTION_ALLOWED_FIELDS = {
    "field": {"name", "acres", "soil_type", "notes"},
    "machine": {"name", "model_year", "serial_number", "hours"},
    "rain": {"year", "date", "month", "mm", "notes"},
    "frost": {"year", "date", "type", "temp_c", "notes"},
    "hail": {"year", "date", "severity", "notes"},
    "crop": {
        "field_id",
        "year",
        "crop",
        "variety",
        "seeded_date",
        "harvested_date",
        "bushels_per_acre",
        "total_bushels",
        "notes",
    },
    "spray": {"field_id", "year", "date", "crop", "products", "acres", "wind", "temp", "operator", "notes"},
    "input": {"field_id", "year", "date", "type", "product", "rate_per_acre", "total_amount", "cost", "notes"},
    "maint": {"machine_id", "year", "date", "type", "description", "parts", "cost", "done_by"},
}


def _build_system_prompt(db: Session, farm_id: int) -> str:
    fields = db.query(models.Field).filter(models.Field.farm_id == farm_id).all()
    machines = db.query(models.Machine).filter(models.Machine.farm_id == farm_id).all()
    field_list = "\n".join(f"  - id={f.id}: {f.name}" for f in fields) or "  (none yet)"
    machine_list = "\n".join(f"  - id={m.id}: {m.name}" for m in machines) or "  (none yet)"
    today = date.today().isoformat()
    current_year = date.today().year

    return f"""You are the data-entry assistant for Prairie Ag Manager, a farm records app for a dryland
grain farm near Magrath, Alberta. A family member will describe something in plain language
(e.g. "sprayed the north field with roundup today, light wind" or "got 12mm of rain last night"
or "combine hit 4200 hours"). Your job is to turn that into ONE structured record for the
correct table, or ask for clarification if the message is not a data-entry statement.

Today's date is {today}. Default year is {current_year} unless the message says otherwise.

Known fields for this farm (match by name, case-insensitive, fuzzy ok):
{field_list}

Known machines for this farm (match by name, case-insensitive, fuzzy ok):
{machine_list}

Respond with ONLY a single JSON object, no markdown fences, no commentary outside the JSON,
matching exactly this shape:

{{"message": "<a short friendly confirmation to show the user, or a clarifying question>",
  "action": "<one of: field, machine, rain, frost, hail, crop, spray, input, maint, none>",
  "record": {{...fields for that action's table...}} or null}}

Rules:
- action "none" means: no record could be confidently created (small talk, ambiguous, or a
  question). Set "record" to null and use "message" to explain or ask a clarifying question.
- action "field" record fields: name (required), acres, soil_type, notes.
- action "machine" record fields: name (required), model_year, serial_number, hours.
- action "rain" record fields: year (required), date (YYYY-MM-DD or null), month (1-12), mm, notes.
- action "frost" record fields: year (required), date, type (one of "Light Frost", "Hard Frost",
  "Late Spring Frost", "First Fall Frost"), temp_c, notes.
- action "hail" record fields: year (required), date, severity (one of "Light", "Moderate",
  "Severe"), notes.
- action "crop" record fields: field_id (match from known fields, or null), year (required), crop,
  variety, seeded_date, harvested_date, bushels_per_acre, total_bushels, notes.
- action "spray" record fields: field_id (match from known fields, or null), year (required),
  date, crop, products, acres, wind, temp, operator, notes.
- action "input" record fields: field_id (match from known fields, or null), year (required),
  date, type (one of "Seed", "Fertilizer", "Herbicide", "Fungicide", "Insecticide", "Fuel",
  "Other"), product, rate_per_acre, total_amount, cost, notes.
- action "maint" record fields: machine_id (match from known machines, or null), year (required),
  date, type, description, parts, cost, done_by.
- If the message references a field or machine name that isn't in the known list, still create
  the record with field_id/machine_id set to null and mention the unmatched name in "notes" if
  reasonable.
- Never invent a field_id or machine_id that isn't in the known lists above.
- Only include keys that are relevant for the chosen action's table; omit unrelated keys.
- "message" should be short (one sentence), warm, and specific about what was recorded.
"""


def _extract_json(text: str) -> dict:
    text = text.strip()
    if text.startswith("```"):
        text = text.strip("`")
        if text.lower().startswith("json"):
            text = text[4:]
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1:
        raise ValueError("No JSON object found in model response")
    return json.loads(text[start : end + 1])


def parse_message(db: Session, farm_id: int, message: str) -> dict:
    if not settings.anthropic_api_key:
        return {
            "message": "Chat parsing isn't configured yet — ask your admin to set ANTHROPIC_API_KEY.",
            "action": "none",
            "record": None,
        }

    client = Anthropic(api_key=settings.anthropic_api_key)
    system_prompt = _build_system_prompt(db, farm_id)

    response = client.messages.create(
        model=settings.anthropic_model,
        max_tokens=1024,
        temperature=0,
        system=system_prompt,
        messages=[{"role": "user", "content": message}],
    )
    raw_text = "".join(block.text for block in response.content if block.type == "text")

    try:
        parsed = _extract_json(raw_text)
    except (ValueError, json.JSONDecodeError):
        return {
            "message": "Sorry, I didn't quite catch that — could you rephrase it?",
            "action": "none",
            "record": None,
        }

    action = parsed.get("action")
    if action not in VALID_ACTIONS:
        action = "none"
    record = parsed.get("record")
    if action == "none" or not isinstance(record, dict):
        record = None

    return {
        "message": parsed.get("message") or "Got it.",
        "action": action,
        "record": record,
    }


def apply_record(db: Session, farm_id: int, action: str, record: dict):
    model = ACTION_TO_MODEL.get(action)
    if model is None or not record:
        return None

    allowed = ACTION_ALLOWED_FIELDS[action]
    clean = {k: v for k, v in record.items() if k in allowed and v is not None}

    if "field_id" in allowed and clean.get("field_id") is not None:
        field = db.get(models.Field, clean["field_id"])
        if field is None or field.farm_id != farm_id:
            clean["field_id"] = None

    if "machine_id" in allowed and clean.get("machine_id") is not None:
        machine = db.get(models.Machine, clean["machine_id"])
        if machine is None or machine.farm_id != farm_id:
            clean["machine_id"] = None

    if "name" in allowed and not clean.get("name"):
        return None
    if "year" in allowed and not clean.get("year"):
        clean["year"] = date.today().year

    item = model(**clean, farm_id=farm_id)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item
