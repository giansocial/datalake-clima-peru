import pytest
import pandas as pd
from src.transform.cleaner import parse_daily_response, clean_weather_df, merge_city_data


RAW_DATA = {
    "daily": {
        "time": ["2024-01-01", "2024-01-02", "2024-01-03"],
        "temperature_2m_max": [28.5, 29.1, None],
        "temperature_2m_min": [20.1, 21.0, None],
        "precipitation_sum": [0.0, 5.2, None],
        "windspeed_10m_max": [10.0, 15.3, None],
    }
}


def test_parse_creates_columns():
    df = parse_daily_response("Lima", "Costa", RAW_DATA)
    expected = {"fecha", "temp_max", "temp_min", "precipitacion_mm", "viento_max_kmh", "ciudad", "region"}
    assert expected == set(df.columns)
    assert len(df) == 3
    assert df["ciudad"].iloc[0] == "Lima"


def test_parse_fecha_is_datetime():
    df = parse_daily_response("Cusco", "Sierra", RAW_DATA)
    assert pd.api.types.is_datetime64_any_dtype(df["fecha"])


def test_clean_removes_duplicates():
    df = parse_daily_response("Lima", "Costa", RAW_DATA)
    df_dup = pd.concat([df, df.iloc[:1]], ignore_index=True)
    cleaned = clean_weather_df(df_dup)
    assert len(cleaned) == 2


def test_clean_removes_all_null_rows():
    raw = {
        "daily": {
            "time": ["2024-01-01", "2024-01-02"],
            "temperature_2m_max": [25.0, None],
            "temperature_2m_min": [18.0, None],
            "precipitation_sum": [1.0, None],
            "windspeed_10m_max": [5.0, None],
        }
    }
    df = parse_daily_response("Ica", "Costa", raw)
    cleaned = clean_weather_df(df)
    assert len(cleaned) == 1


def test_clean_coerces_numeric():
    raw = {
        "daily": {
            "time": ["2024-01-01"],
            "temperature_2m_max": ["abc"],
            "temperature_2m_min": [18.0],
            "precipitation_sum": [0.0],
            "windspeed_10m_max": [5.0],
        }
    }
    df = parse_daily_response("Puno", "Sierra", raw)
    cleaned = clean_weather_df(df)
    assert pd.isna(cleaned["temp_max"].iloc[0])


def test_merge_combines_cities():
    results = {
        "Lima": RAW_DATA,
        "Cusco": RAW_DATA,
    }
    config = {
        "Lima": {"lat": -12, "lon": -77, "region": "Costa"},
        "Cusco": {"lat": -13, "lon": -71, "region": "Sierra"},
    }
    merged = merge_city_data(results, config)
    assert "Lima" in merged["ciudad"].values
    assert "Cusco" in merged["ciudad"].values


def test_merge_empty_returns_empty():
    df = merge_city_data({}, {})
    assert df.empty


def test_clean_preserves_partial_nulls():
    raw = {
        "daily": {
            "time": ["2024-01-01"],
            "temperature_2m_max": [30.0],
            "temperature_2m_min": [None],
            "precipitation_sum": [0.0],
            "windspeed_10m_max": [5.0],
        }
    }
    df = parse_daily_response("Tacna", "Costa", raw)
    cleaned = clean_weather_df(df)
    assert len(cleaned) == 1
