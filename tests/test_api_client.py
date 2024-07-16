import pytest
from unittest.mock import patch, MagicMock
from src.extract.api_client import fetch_daily_weather, fetch_city_batch


def _mock_response(data, status=200):
    resp = MagicMock()
    resp.status_code = status
    resp.json.return_value = data
    resp.raise_for_status.return_value = None
    return resp


SAMPLE_RESPONSE = {
    "daily": {
        "time": ["2024-01-01", "2024-01-02"],
        "temperature_2m_max": [25.3, 26.1],
        "temperature_2m_min": [18.2, 19.0],
        "precipitation_sum": [0.0, 1.2],
        "windspeed_10m_max": [12.5, 8.3],
    }
}


@patch("src.extract.api_client.requests.get")
def test_fetch_weather_ok(mock_get):
    mock_get.return_value = _mock_response(SAMPLE_RESPONSE)
    data = fetch_daily_weather(-12.04, -77.04, "2024-01-01", "2024-01-02")
    assert "daily" in data
    assert len(data["daily"]["time"]) == 2


@patch("src.extract.api_client.requests.get")
def test_fetch_weather_no_daily_key(mock_get):
    mock_get.return_value = _mock_response({"error": True})
    with pytest.raises(ValueError, match="sin datos diarios"):
        fetch_daily_weather(-12.04, -77.04, "2024-01-01", "2024-01-02")


@patch("src.extract.api_client.requests.get")
def test_fetch_weather_retry_on_error(mock_get):
    import requests as req
    mock_get.side_effect = [
        req.exceptions.ConnectionError("timeout"),
        _mock_response(SAMPLE_RESPONSE),
    ]
    data = fetch_daily_weather(-12.04, -77.04, "2024-01-01", "2024-01-02")
    assert "daily" in data
    assert mock_get.call_count == 2


@patch("src.extract.api_client.requests.get")
def test_fetch_weather_max_retries(mock_get):
    import requests as req
    mock_get.side_effect = req.exceptions.ConnectionError("fallo red")
    with pytest.raises(ConnectionError, match="fallo tras"):
        fetch_daily_weather(-12.04, -77.04, "2024-01-01", "2024-01-02")


@patch("src.extract.api_client.fetch_daily_weather")
def test_batch_returns_all_cities(mock_fetch):
    mock_fetch.return_value = SAMPLE_RESPONSE
    cities = {
        "Lima": {"lat": -12.04, "lon": -77.04, "region": "Costa"},
        "Cusco": {"lat": -13.53, "lon": -71.96, "region": "Sierra"},
    }
    results = fetch_city_batch(cities, "2024-01-01", "2024-01-02", rate_limit=0)
    assert len(results) == 2
    assert "Lima" in results
    assert "Cusco" in results


@patch("src.extract.api_client.fetch_daily_weather")
def test_batch_empty_cities(mock_fetch):
    results = fetch_city_batch({}, "2024-01-01", "2024-01-02", rate_limit=0)
    assert results == {}
    mock_fetch.assert_not_called()
