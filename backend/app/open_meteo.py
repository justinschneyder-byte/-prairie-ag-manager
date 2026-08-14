"""
Regional weather for Magrath, AB via Open-Meteo (open-meteo.com) — free, no API
key. This is external reference data, separate from the farm's own logged
rain_events. Responses are cached in the weather_cache table: indefinitely for
closed past years (that data won't change), 24h for the current year and the
forecast (both still moving targets).
"""

import json
from collections import defaultdict
from datetime import date, datetime, timedelta, timezone

import httpx
from sqlalchemy.orm import Session

from . import models

MAGRATH_LAT = 49.4267
MAGRATH_LON = -112.8611
TIMEZONE = "America/Edmonton"

ARCHIVE_URL = "https://archive-api.open-meteo.com/v1/archive"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"

FORECAST_CACHE_KEY = "forecast"
FORECAST_TTL = timedelta(hours=24)
CURRENT_YEAR_ARCHIVE_TTL = timedelta(hours=24)


def _get_cached(db: Session, key: str, ttl: timedelta | None):
    row = db.query(models.WeatherCache).filter(models.WeatherCache.cache_key == key).first()
    if row is None:
        return None
    if ttl is not None:
        fetched_at = row.fetched_at
        if fetched_at.tzinfo is None:
            fetched_at = fetched_at.replace(tzinfo=timezone.utc)
        if datetime.now(timezone.utc) - fetched_at > ttl:
            return None
    return json.loads(row.payload)


def _set_cached(db: Session, key: str, payload: dict):
    row = db.query(models.WeatherCache).filter(models.WeatherCache.cache_key == key).first()
    if row is None:
        db.add(models.WeatherCache(cache_key=key, payload=json.dumps(payload)))
    else:
        row.payload = json.dumps(payload)
        row.fetched_at = datetime.now(timezone.utc)
    db.commit()


def _aggregate_monthly(daily: dict) -> list[dict]:
    months = defaultdict(lambda: {"precip": 0.0, "highs": [], "lows": []})
    times = daily.get("time", [])
    precip = daily.get("precipitation_sum", [])
    highs = daily.get("temperature_2m_max", [])
    lows = daily.get("temperature_2m_min", [])

    for i, date_str in enumerate(times):
        month = int(date_str[5:7])
        if i < len(precip) and precip[i] is not None:
            months[month]["precip"] += precip[i]
        if i < len(highs) and highs[i] is not None:
            months[month]["highs"].append(highs[i])
        if i < len(lows) and lows[i] is not None:
            months[month]["lows"].append(lows[i])

    result = []
    for month in range(1, 13):
        m = months.get(month)
        if not m or (not m["highs"] and not m["precip"]):
            result.append({"month": month, "precip_mm": None, "temp_high_avg": None, "temp_low_avg": None})
            continue
        result.append(
            {
                "month": month,
                "precip_mm": round(m["precip"], 1),
                "temp_high_avg": round(sum(m["highs"]) / len(m["highs"]), 1) if m["highs"] else None,
                "temp_low_avg": round(sum(m["lows"]) / len(m["lows"]), 1) if m["lows"] else None,
            }
        )
    return result


def get_regional_history(db: Session, year: int) -> dict:
    current_year = datetime.now(timezone.utc).year
    cache_key = f"archive:{year}"
    ttl = CURRENT_YEAR_ARCHIVE_TTL if year >= current_year else None

    cached = _get_cached(db, cache_key, ttl)
    if cached is not None:
        return cached

    start_date = f"{year}-01-01"
    end_date = f"{year}-12-31" if year < current_year else date.today().isoformat()

    try:
        resp = httpx.get(
            ARCHIVE_URL,
            params={
                "latitude": MAGRATH_LAT,
                "longitude": MAGRATH_LON,
                "start_date": start_date,
                "end_date": end_date,
                "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum",
                "timezone": TIMEZONE,
            },
            timeout=15,
        )
        resp.raise_for_status()
        data = resp.json()
    except httpx.HTTPError as exc:
        raise RuntimeError(f"Could not reach Open-Meteo archive API: {exc}") from exc

    result = {
        "year": year,
        "months": _aggregate_monthly(data.get("daily", {})),
        "source": "Open-Meteo (archive-api.open-meteo.com)",
        "fetched_at": datetime.now(timezone.utc).isoformat(),
    }
    _set_cached(db, cache_key, result)
    return result


def get_regional_forecast(db: Session, days: int = 10) -> dict:
    cached = _get_cached(db, FORECAST_CACHE_KEY, FORECAST_TTL)
    if cached is not None:
        return cached

    try:
        resp = httpx.get(
            FORECAST_URL,
            params={
                "latitude": MAGRATH_LAT,
                "longitude": MAGRATH_LON,
                "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum,precipitation_probability_max",
                "forecast_days": days,
                "timezone": TIMEZONE,
            },
            timeout=15,
        )
        resp.raise_for_status()
        data = resp.json()
    except httpx.HTTPError as exc:
        raise RuntimeError(f"Could not reach Open-Meteo forecast API: {exc}") from exc

    daily = data.get("daily", {})
    times = daily.get("time", [])
    highs = daily.get("temperature_2m_max", [])
    lows = daily.get("temperature_2m_min", [])
    precip = daily.get("precipitation_sum", [])
    prob = daily.get("precipitation_probability_max", [])

    days_out = [
        {
            "date": date_str,
            "temp_high": highs[i] if i < len(highs) else None,
            "temp_low": lows[i] if i < len(lows) else None,
            "precip_mm": precip[i] if i < len(precip) else None,
            "precip_probability": prob[i] if i < len(prob) else None,
        }
        for i, date_str in enumerate(times)
    ]

    result = {
        "days": days_out,
        "source": "Open-Meteo (api.open-meteo.com)",
        "fetched_at": datetime.now(timezone.utc).isoformat(),
    }
    _set_cached(db, FORECAST_CACHE_KEY, result)
    return result
