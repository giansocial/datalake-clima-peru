import pytest
import pandas as pd
import numpy as np
from src.transform.enricher import (
    add_thermal_amplitude,
    add_monthly_stats,
    classify_climate_zone,
    add_climate_classification,
    detect_extreme_events,
)


def _sample_df():
    dates = pd.date_range("2024-01-01", periods=90, freq="D")
    np.random.seed(42)
    return pd.DataFrame({
        "fecha": dates,
        "ciudad": "Lima",
        "region": "Costa",
        "temp_max": np.random.uniform(24, 32, 90),
        "temp_min": np.random.uniform(16, 22, 90),
        "precipitacion_mm": np.random.exponential(0.5, 90),
        "viento_max_kmh": np.random.uniform(5, 20, 90),
    })


def test_thermal_amplitude():
    df = _sample_df()
    result = add_thermal_amplitude(df)
    assert "amplitud_termica" in result.columns
    for i in range(len(result)):
        expected = result["temp_max"].iloc[i] - result["temp_min"].iloc[i]
        assert abs(result["amplitud_termica"].iloc[i] - expected) < 0.01


def test_thermal_amplitude_no_mutation():
    df = _sample_df()
    original_cols = list(df.columns)
    add_thermal_amplitude(df)
    assert list(df.columns) == original_cols


def test_monthly_stats_columns():
    df = _sample_df()
    monthly = add_monthly_stats(df)
    expected = {"ciudad", "anio", "mes", "temp_max_prom", "temp_min_prom",
                "precip_total", "precip_dias", "viento_max_prom"}
    assert expected == set(monthly.columns)


def test_monthly_stats_grouping():
    df = _sample_df()
    monthly = add_monthly_stats(df)
    assert len(monthly) <= 12
    assert monthly["anio"].iloc[0] == 2024


def test_classify_tropical():
    row = pd.Series({"temp_max_prom": 30, "precip_total": 250})
    assert classify_climate_zone(row) == "tropical_humedo"


def test_classify_desert():
    row = pd.Series({"temp_max_prom": 27, "precip_total": 10})
    assert classify_climate_zone(row) == "desertico_calido"


def test_classify_cold():
    row = pd.Series({"temp_max_prom": 10, "precip_total": 50})
    assert classify_climate_zone(row) == "frio_altiplano"


def test_classify_rainy():
    row = pd.Series({"temp_max_prom": 20, "precip_total": 200})
    assert classify_climate_zone(row) == "lluvioso"


def test_classify_temperate():
    row = pd.Series({"temp_max_prom": 22, "precip_total": 80})
    assert classify_climate_zone(row) == "templado"


def test_climate_classification_adds_column():
    df = _sample_df()
    monthly = add_monthly_stats(df)
    result = add_climate_classification(monthly)
    assert "zona_climatica" in result.columns


def test_detect_extreme_events():
    dates = pd.date_range("2024-01-01", periods=365, freq="D")
    np.random.seed(123)
    temps_max = np.random.normal(27, 2, 365)
    temps_max[100] = 40.0
    temps_min = np.random.normal(18, 2, 365)
    temps_min[200] = 2.0
    precip = np.random.exponential(1, 365)
    precip[50] = 80.0
    df = pd.DataFrame({
        "fecha": dates,
        "ciudad": "Lima",
        "temp_max": temps_max,
        "temp_min": temps_min,
        "precipitacion_mm": precip,
    })
    events = detect_extreme_events(df)
    assert not events.empty
    tipos = events["tipo"].unique()
    assert "ola_calor" in tipos


def test_detect_no_events_uniform_data():
    dates = pd.date_range("2024-01-01", periods=30, freq="D")
    df = pd.DataFrame({
        "fecha": dates,
        "ciudad": "Test",
        "temp_max": [25.0] * 30,
        "temp_min": [18.0] * 30,
        "precipitacion_mm": [1.0] * 30,
    })
    events = detect_extreme_events(df)
    assert events.empty
