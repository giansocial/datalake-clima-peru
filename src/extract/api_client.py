import time
import logging
import requests
from typing import Optional

from src.config.settings import (
    ARCHIVE_URL,
    DAILY_VARIABLES,
    REQUEST_TIMEOUT,
    MAX_RETRIES,
    RETRY_BACKOFF,
)

log = logging.getLogger(__name__)


def fetch_daily_weather(
    lat: float,
    lon: float,
    start_date: str,
    end_date: str,
    variables: Optional[list[str]] = None,
) -> dict:
    params = {
        "latitude": lat,
        "longitude": lon,
        "start_date": start_date,
        "end_date": end_date,
        "daily": ",".join(variables or DAILY_VARIABLES),
        "timezone": "America/Lima",
    }
    last_err = None
    for attempt in range(MAX_RETRIES):
        try:
            resp = requests.get(ARCHIVE_URL, params=params, timeout=REQUEST_TIMEOUT)
            resp.raise_for_status()
            data = resp.json()
            if "daily" not in data:
                raise ValueError(f"respuesta sin datos diarios: {list(data.keys())}")
            return data
        except requests.exceptions.HTTPError as e:
            if resp.status_code == 429:
                wait = RETRY_BACKOFF * (2 ** attempt)
                log.warning("rate limit, esperando %.1fs", wait)
                time.sleep(wait)
                last_err = e
                continue
            raise
        except requests.exceptions.RequestException as e:
            wait = RETRY_BACKOFF * (2 ** attempt)
            log.warning("error request (intento %d): %s", attempt + 1, e)
            time.sleep(wait)
            last_err = e
    raise ConnectionError(f"fallo tras {MAX_RETRIES} intentos: {last_err}")


def fetch_city_batch(
    cities: dict,
    start_date: str,
    end_date: str,
    rate_limit: float = 1.2,
) -> dict[str, dict]:
    results = {}
    total = len(cities)
    for i, (city, info) in enumerate(cities.items(), 1):
        log.info("[%d/%d] descargando %s...", i, total, city)
        data = fetch_daily_weather(
            lat=info["lat"],
            lon=info["lon"],
            start_date=start_date,
            end_date=end_date,
        )
        results[city] = data
        if i < total:
            time.sleep(rate_limit)
    return results
