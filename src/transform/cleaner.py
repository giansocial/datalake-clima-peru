import logging
import pandas as pd
from typing import Optional

log = logging.getLogger(__name__)


def parse_daily_response(city: str, region: str, raw: dict) -> pd.DataFrame:
    daily = raw["daily"]
    df = pd.DataFrame({
        "fecha": pd.to_datetime(daily["time"]),
        "temp_max": daily.get("temperature_2m_max"),
        "temp_min": daily.get("temperature_2m_min"),
        "precipitacion_mm": daily.get("precipitation_sum"),
        "viento_max_kmh": daily.get("windspeed_10m_max"),
    })
    df["ciudad"] = city
    df["region"] = region
    return df


def clean_weather_df(df: pd.DataFrame) -> pd.DataFrame:
    before = len(df)
    df = df.drop_duplicates(subset=["fecha", "ciudad"])
    dupes = before - len(df)
    if dupes > 0:
        log.info("eliminados %d duplicados", dupes)

    numeric_cols = ["temp_max", "temp_min", "precipitacion_mm", "viento_max_kmh"]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    null_rows = df[numeric_cols].isnull().all(axis=1).sum()
    if null_rows > 0:
        df = df[~df[numeric_cols].isnull().all(axis=1)]
        log.info("eliminadas %d filas completamente nulas", null_rows)

    return df.reset_index(drop=True)


def merge_city_data(
    city_results: dict[str, dict],
    cities_config: dict,
) -> pd.DataFrame:
    frames = []
    for city, raw in city_results.items():
        region = cities_config[city]["region"]
        df = parse_daily_response(city, region, raw)
        frames.append(df)
    if not frames:
        return pd.DataFrame()
    merged = pd.concat(frames, ignore_index=True)
    return clean_weather_df(merged)
