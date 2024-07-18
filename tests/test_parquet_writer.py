import pytest
import pandas as pd
from pathlib import Path
from src.load.parquet_writer import write_partitioned, read_lake, lake_stats


@pytest.fixture
def sample_df():
    return pd.DataFrame({
        "ciudad": ["Lima", "Lima", "Cusco", "Cusco"],
        "region": ["Costa", "Costa", "Sierra", "Sierra"],
        "fecha": pd.date_range("2024-01-01", periods=4, freq="D"),
        "temp_max": [28.0, 29.0, 20.0, 21.0],
    })


def test_write_no_partition(tmp_path, sample_df):
    files = write_partitioned(sample_df, tmp_path, [], name="test")
    assert len(files) == 1
    assert files[0].suffix == ".parquet"
    loaded = pd.read_parquet(files[0])
    assert len(loaded) == 4


def test_write_single_partition(tmp_path, sample_df):
    files = write_partitioned(sample_df, tmp_path, ["region"], name="test")
    assert len(files) == 2
    for f in files:
        loaded = pd.read_parquet(f)
        assert len(loaded) == 2


def test_write_multi_partition(tmp_path, sample_df):
    files = write_partitioned(sample_df, tmp_path, ["region", "ciudad"], name="test")
    assert len(files) == 2


def test_read_lake_all(tmp_path, sample_df):
    write_partitioned(sample_df, tmp_path, ["region"], name="data")
    result = read_lake(tmp_path)
    assert len(result) == 4


def test_read_lake_filter(tmp_path, sample_df):
    write_partitioned(sample_df, tmp_path, [], name="data")
    result = read_lake(tmp_path, filters={"ciudad": "Lima"})
    assert len(result) == 2
    assert (result["ciudad"] == "Lima").all()


def test_read_lake_empty(tmp_path):
    result = read_lake(tmp_path)
    assert result.empty


def test_lake_stats_count(tmp_path, sample_df):
    write_partitioned(sample_df, tmp_path, ["ciudad"], name="data")
    stats = lake_stats(tmp_path)
    assert stats["archivos"] == 2
    assert stats["filas_totales"] == 4
    assert stats["tamano_mb"] > 0
    assert "Lima" in stats["ciudades"]
    assert "Cusco" in stats["ciudades"]
