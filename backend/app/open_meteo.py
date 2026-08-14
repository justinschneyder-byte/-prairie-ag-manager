"""
Regional weather for Magrath, AB via Open-Meteo (open-meteo.com) — free, no API
key. This is external reference data, separate from the farm's own logged
rain_events/frost_events. Responses are cached in the weather_cache table:
indefinitely for closed past years (that data won't change), 24h for the
current year and the forecast (both still moving targets).

Note: no regional hail data — Open-Meteo's hail variables only cover Central
Europe, not Alberta. Hail stays manual-entry-only (hail_events table).
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

# Bumped when the cached response shape changes, so old cached rows (e.g. from
# before wind/frost were added) get a fresh fetch instead of serving stale shape.
CACHE_VERSION = "v2"
FORECAST_CACHE_KEY = f"forecast:{CACHE_VERSION}"
FORECAST_TTL = timedelta(hours=24)
CURRENT_YEAR_ARCHIVE_TTL = timedelta(hours=24)

FROST_THRESHOLD_C = 0


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
    months = defaultdict(lambda: {"precip": 0.0, "highs": [], "lows": [], "winds": [], "frost_days": 0})
    times = daily.get("time", [])
    precip = daily.get("precipitation_sum", [])
    highs = daily.get("temperature_2m_max", [])
    lows = daily.get("temperature_2m_min", [])
    winds = daily.get("wind_speed_10m_max", [])

    for i, date_str in enumerate(times):
        month = int(date_str[5:7])
        if i < len(precip) and precip[i] is not None:
            months[month]["precip"] += precip[i]
        if i < len(highs) and highs[i] is not None:
            months[month]["highs"].append(highs[i])
        if i < len(lows) and lows[i] is not None:
            months[month]["lows"].append(lows[i])
            if lows[i] <= FROST_THRESHOLD_C:
                months[month]["frost_days"] += 1
        if i < len(winds) and winds[i] is not None:
            months[month]["winds"].append(winds[i])

    result = []
    for month in range(1, 13):
        m = months.get(month)
        if not m or (not m["highs"] and not m["precip"]):
            result.append(
                {
                    "month": month,
                    "precip_mm": None,
                    "temp_high_avg": None,
                    "temp_low_avg": None,
                    "wind_speed_avg": None,
                    "frost_days": 0,
                }
            )
            continue
        result.append(
            {
                "month": month,
                "precip_mm": round(m["precip"], 1),
                "temp_high_avg": round(sum(m["highs"]) / len(m["highs"]), 1) if m["highs"] else None,
                "temp_low_avg": round(sum(m["lows"]) / len(m["lows"]), 1) if m["lows"] else None,
                "wind_speed_avg": round(sum(m["winds"]) / len(m["winds"]), 1) if m["winds"] else None,
                "frost_days": m["frost_days"],
            }
        )
    return result


def _compute_frost_summary(daily: dict) -> dict:
    times = daily.get("time", [])
    lows = daily.get("temperature_2m_min", [])

    frost_dates = [
        date_str for i, date_str in enumerate(times) if i < len(lows) and lows[i] is not None and lows[i] <= FROST_THRESHOLD_C
    ]

    # "Spring" = first half of year, "fall" = second half — matches the app's
    # own Frost Events categories (Late Spring Frost / First Fall Frost).
    spring_frosts = [d for d in frost_dates if int(d[5:7]) <= 6]
    fall_frosts = [d for d in frost_dates if int(d[5:7]) >= 7]

    return {
        "total_frost_days": len(frost_dates),
        "last_spring_frost": max(spring_frosts) if spring_frosts else None,
        "first_fall_frost": min(fall_frosts) if fall_frosts else None,
    }


def get_regional_history(db: Session, year: int) -> dict:
    current_year = datetime.now(timezone.utc).year
    cache_key = f"archive:{CACHE_VERSION}:{year}"
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
                "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum,wind_speed_10m_max,wind_direction_10m_dominant",
                "timezone": TIMEZONE,
            },
            timeout=15,
        )
        resp.raise_for_status()
        data = resp.json()
    except httpx.HTTPError as exc:
        raise RuntimeError(f"Could not reach Open-Meteo archive API: {exc}") from exc

    daily = data.get("daily", {})
    result = {
        "year": year,
        "months": _aggregate_monthly(daily),
        "frost_summary": _compute_frost_summary(daily),
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
                "daily": (
                    "temperature_2m_max,temperature_2m_min,precipitation_sum,precipitation_probability_max,"
                    "wind_speed_10m_max,wind_direction_10m_dominant"
                ),
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
    wind_speed = daily.get("wind_speed_10m_max", [])
    wind_dir = daily.get("wind_direction_10m_dominant", [])

    days_out = [
        {
            "date": date_str,
            "temp_high": highs[i] if i < len(highs) else None,
            "temp_low": lows[i] if i < len(lows) else None,
            "precip_mm": precip[i] if i < len(precip) else None,
            "precip_probability": prob[i] if i < len(prob) else None,
            "wind_speed_max": wind_speed[i] if i < len(wind_speed) else None,
            "wind_direction": wind_dir[i] if i < len(wind_dir) else None,
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
