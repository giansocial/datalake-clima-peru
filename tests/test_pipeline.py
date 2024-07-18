import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path
from src.pipeline import run_pipeline, save_raw_json


MOCK_RAW = {
    "daily": {
        "time": ["2024-01-01", "2024-01-02", "2024-01-03"],
        "temperature_2m_max": [28.5, 29.1, 27.8],
        "temperature_2m_min": [20.1, 21.0, 19.5],
        "precipitation_sum": [0.0, 5.2, 0.3],
        "windspeed_10m_max": [10.0, 15.3, 8.1],
    }
}

TEST_CITIES = {
    "Lima": {"lat": -12.04, "lon": -77.04, "region": "Costa"},
    "Cusco": {"lat": -13.53, "lon": -71.96, "region": "Sierra"},
}


def test_save_raw_json(tmp_path):
    data = {"Lima": MOCK_RAW}
    save_raw_json(data, tmp_path)
    assert (tmp_path / "lima.json").exists()


def test_save_raw_json_special_chars(tmp_path):
    data = {"Cerro de Pasco": MOCK_RAW}
    save_raw_json(data, tmp_path)
    assert (tmp_path / "cerro_de_pasco.json").exists()


@patch("src.pipeline.fetch_city_batch")
def test_pipeline_returns_stats(mock_fetch, tmp_path):
    mock_fetch.return_value = {c: MOCK_RAW for c in TEST_CITIES}
    with patch("src.pipeline.DATA_RAW", tmp_path / "raw"), \
         patch("src.pipeline.DATA_LAKE", tmp_path / "lake"), \
         patch("src.pipeline.DATA_PROCESSED", tmp_path / "processed"):
        (tmp_path / "processed").mkdir(parents=True, exist_ok=True)
        result = run_pipeline(TEST_CITIES, "2024-01-01", "2024-01-03")
    assert result["num_ciudades"] == 2
    assert result["registros_diarios"] == 6


@patch("src.pipeline.fetch_city_batch")
def test_pipeline_creates_lake_files(mock_fetch, tmp_path):
    mock_fetch.return_value = {c: MOCK_RAW for c in TEST_CITIES}
    with patch("src.pipeline.DATA_RAW", tmp_path / "raw"), \
         patch("src.pipeline.DATA_LAKE", tmp_path / "lake"), \
         patch("src.pipeline.DATA_PROCESSED", tmp_path / "processed"):
        (tmp_path / "processed").mkdir(parents=True, exist_ok=True)
        run_pipeline(TEST_CITIES, "2024-01-01", "2024-01-03")
    parquets = list((tmp_path / "lake").rglob("*.parquet"))
    assert len(parquets) > 0


@patch("src.pipeline.fetch_city_batch")
def test_pipeline_creates_csv(mock_fetch, tmp_path):
    mock_fetch.return_value = {c: MOCK_RAW for c in TEST_CITIES}
    with patch("src.pipeline.DATA_RAW", tmp_path / "raw"), \
         patch("src.pipeline.DATA_LAKE", tmp_path / "lake"), \
         patch("src.pipeline.DATA_PROCESSED", tmp_path / "processed"):
        (tmp_path / "processed").mkdir(parents=True, exist_ok=True)
        run_pipeline(TEST_CITIES, "2024-01-01", "2024-01-03")
    assert (tmp_path / "processed" / "resumen_mensual.csv").exists()
