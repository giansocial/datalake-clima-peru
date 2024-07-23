from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent

DATA_RAW = BASE_DIR / "data" / "raw"
DATA_LAKE = BASE_DIR / "data" / "lake"
DATA_PROCESSED = BASE_DIR / "data" / "processed"
LOG_DIR = BASE_DIR / "logs"

for _d in (DATA_RAW, DATA_LAKE, DATA_PROCESSED, LOG_DIR):
    _d.mkdir(parents=True, exist_ok=True)

FORECAST_URL = "https://api.open-meteo.com/v1/forecast"
ARCHIVE_URL = "https://archive-api.open-meteo.com/v1/archive"

DAILY_VARIABLES = [
    "temperature_2m_max",
    "temperature_2m_min",
    "precipitation_sum",
    "windspeed_10m_max",
]

REQUEST_TIMEOUT = 30
MAX_RETRIES = 3
RETRY_BACKOFF = 2.0

CITIES = {
    "Lima": {"lat": -12.0464, "lon": -77.0428, "region": "Costa"},
    "Arequipa": {"lat": -16.4090, "lon": -71.5375, "region": "Sierra"},
    "Cusco": {"lat": -13.5320, "lon": -71.9675, "region": "Sierra"},
    "Trujillo": {"lat": -8.1116, "lon": -79.0288, "region": "Costa"},
    "Chiclayo": {"lat": -6.7714, "lon": -79.8409, "region": "Costa"},
    "Piura": {"lat": -5.1945, "lon": -80.6328, "region": "Costa"},
    "Iquitos": {"lat": -3.7491, "lon": -73.2538, "region": "Selva"},
    "Huancayo": {"lat": -12.0651, "lon": -75.2049, "region": "Sierra"},
    "Tacna": {"lat": -18.0146, "lon": -70.2536, "region": "Costa"},
    "Puno": {"lat": -15.8402, "lon": -70.0219, "region": "Sierra"},
    "Ayacucho": {"lat": -13.1588, "lon": -74.2236, "region": "Sierra"},
    "Cajamarca": {"lat": -7.1638, "lon": -78.5003, "region": "Sierra"},
    "Chimbote": {"lat": -9.0853, "lon": -78.5783, "region": "Costa"},
    "Ica": {"lat": -14.0678, "lon": -75.7286, "region": "Costa"},
    "Juliaca": {"lat": -15.5000, "lon": -70.1333, "region": "Sierra"},
    "Huaraz": {"lat": -9.5279, "lon": -77.5278, "region": "Sierra"},
    "Pucallpa": {"lat": -8.3791, "lon": -74.5539, "region": "Selva"},
    "Tarapoto": {"lat": -6.4874, "lon": -76.3600, "region": "Selva"},
    "Tumbes": {"lat": -3.5669, "lon": -80.4515, "region": "Costa"},
    "Moyobamba": {"lat": -6.0349, "lon": -76.9713, "region": "Selva"},
    "Huanuco": {"lat": -9.9306, "lon": -76.2422, "region": "Sierra"},
    "Cerro de Pasco": {"lat": -10.6868, "lon": -76.2625, "region": "Sierra"},
    "Puerto Maldonado": {"lat": -12.5933, "lon": -69.1891, "region": "Selva"},
    "Chachapoyas": {"lat": -6.2316, "lon": -77.8691, "region": "Selva"},
    "Abancay": {"lat": -13.6339, "lon": -72.8814, "region": "Sierra"},
    "Moquegua": {"lat": -17.1940, "lon": -70.9356, "region": "Costa"},
}

DEFAULT_START_DATE = "2024-01-01"
DEFAULT_END_DATE = "2024-12-31"
