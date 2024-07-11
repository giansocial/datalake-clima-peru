import pandas as pd
import numpy as np


def add_thermal_amplitude(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["amplitud_termica"] = df["temp_max"] - df["temp_min"]
    return df


def add_monthly_stats(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["anio"] = df["fecha"].dt.year
    df["mes"] = df["fecha"].dt.month

    monthly = (
        df.groupby(["ciudad", "anio", "mes"])
        .agg(
            temp_max_prom=("temp_max", "mean"),
            temp_min_prom=("temp_min", "mean"),
            precip_total=("precipitacion_mm", "sum"),
            precip_dias=("precipitacion_mm", lambda x: (x > 0.1).sum()),
            viento_max_prom=("viento_max_kmh", "mean"),
        )
        .round(2)
        .reset_index()
    )
    return monthly


def classify_climate_zone(row: pd.Series) -> str:
    temp = row.get("temp_max_prom", 0)
    precip = row.get("precip_total", 0)
    if temp > 28 and precip > 200:
        return "tropical_humedo"
    if temp > 25 and precip < 50:
        return "desertico_calido"
    if temp < 15:
        return "frio_altiplano"
    if precip > 150:
        return "lluvioso"
    return "templado"


def add_climate_classification(monthly: pd.DataFrame) -> pd.DataFrame:
    monthly = monthly.copy()
    monthly["zona_climatica"] = monthly.apply(classify_climate_zone, axis=1)
    return monthly


def detect_extreme_events(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    events = []
    for city, group in df.groupby("ciudad"):
        temp_mean = group["temp_max"].mean()
        temp_std = group["temp_max"].std()
        if temp_std == 0:
            continue
        hot = group[group["temp_max"] > temp_mean + 2 * temp_std]
        for _, row in hot.iterrows():
            events.append({
                "ciudad": city,
                "fecha": row["fecha"],
                "tipo": "ola_calor",
                "valor": row["temp_max"],
                "umbral": round(temp_mean + 2 * temp_std, 1),
            })
        cold = group[group["temp_min"] < group["temp_min"].mean() - 2 * group["temp_min"].std()]
        for _, row in cold.iterrows():
            events.append({
                "ciudad": city,
                "fecha": row["fecha"],
                "tipo": "helada",
                "valor": row["temp_min"],
                "umbral": round(group["temp_min"].mean() - 2 * group["temp_min"].std(), 1),
            })
        heavy_rain = group[group["precipitacion_mm"] > group["precipitacion_mm"].quantile(0.99)]
        for _, row in heavy_rain.iterrows():
            events.append({
                "ciudad": city,
                "fecha": row["fecha"],
                "tipo": "lluvia_extrema",
                "valor": row["precipitacion_mm"],
                "umbral": round(group["precipitacion_mm"].quantile(0.99), 1),
            })
    return pd.DataFrame(events)
