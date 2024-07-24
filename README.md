# Data Lake Climático - Perú

¿Sabías que Perú concentra 28 de los 32 climas del mundo según la clasificación de Köppen? En un solo país puedes encontrar desiertos donde no llueve en décadas, selvas con 4,000 mm de precipitación anual y ciudades a 4,300 msnm donde la temperatura oscila 25°C en un mismo día.

Soy Gian Cruz. Construí este pipeline para capturar esa diversidad climática en un data lake estructurado. Consume la API abierta de Open-Meteo para 26 ciudades del Perú, almacena los datos en formato Parquet particionado por región y ciudad, y genera métricas de amplitud térmica, clasificación climática y detección de eventos extremos a lo largo de Costa, Sierra y Selva.

## Qué hace

- Descarga datos climáticos diarios de Open-Meteo (archivo histórico)
- Limpia y valida registros eliminando duplicados y valores nulos
- Calcula amplitud térmica, promedios mensuales y días de lluvia
- Clasifica zonas climáticas por ciudad y mes
- Detecta eventos extremos: olas de calor, heladas, lluvias atípicas
- Almacena todo en un data lake Parquet particionado

## Estructura del lake

```
data/lake/
├── daily/
│   ├── region=Costa/
│   │   ├── ciudad=Lima/weather.parquet
│   │   ├── ciudad=Trujillo/weather.parquet
│   │   └── ...
│   └── region=Sierra/
│       ├── ciudad=Cusco/weather.parquet
│       └── ...
├── monthly/
│   ├── ciudad=Lima/stats.parquet
│   └── ...
└── events/
    ├── tipo=ola_calor/extreme.parquet
    ├── tipo=helada/extreme.parquet
    └── tipo=lluvia_extrema/extreme.parquet
```

## Instalación

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Uso

```bash
# Pipeline completo (26 ciudades, año 2024)
python -m src.pipeline

# Ciudades específicas
python -m src.pipeline --cities Lima Cusco Iquitos

# Rango de fechas personalizado
python -m src.pipeline --start 2023-06-01 --end 2023-12-31
```

## Tests

```bash
pytest tests/ -v
pytest tests/ --cov=src --cov-report=term-missing
```

## Stack

- Python 3.10+
- pandas + numpy para procesamiento
- requests para consumo de API
- pyarrow para escritura/lectura Parquet
- pytest para testing

## Estructura del proyecto

```
datalake-clima-peru/
├── src/
│   ├── config/
│   │   └── settings.py        # Ciudades, URLs, parámetros
│   ├── extract/
│   │   └── api_client.py       # Cliente Open-Meteo con retry
│   ├── transform/
│   │   ├── cleaner.py          # Limpieza y merge de datos
│   │   └── enricher.py         # Métricas y detección de eventos
│   ├── load/
│   │   └── parquet_writer.py   # Escritura particionada al lake
│   ├── utils/
│   │   └── logger.py
│   └── pipeline.py             # Orquestador principal (CLI)
├── tests/
├── data/
│   ├── raw/                    # JSON crudos por ciudad
│   ├── lake/                   # Parquet particionado
│   └── processed/              # CSVs de resumen
└── requirements.txt
```

---

## What it does

Pipeline that builds a climate data lake for 26 Peruvian cities using Open-Meteo historical archive API. Data is stored as partitioned Parquet files organized by region and city.

Peru has 28 of the 32 world climates (Köppen classification). This project captures that diversity by analyzing temperature, precipitation, wind and extreme weather events across the three natural regions: Coast, Highlands, and Jungle.

## Features

- Daily weather data extraction from Open-Meteo archive API
- Data cleaning with duplicate removal and null handling
- Thermal amplitude calculation and monthly aggregation
- Climate zone classification per city/month
- Extreme event detection (heat waves, frost, heavy rainfall)
- Partitioned Parquet data lake storage

---

## Fuentes de datos

| Fuente | Descripción | Enlace |
|--------|-------------|--------|
| Open-Meteo Archive API | Datos climáticos históricos diarios (temperatura, precipitación, viento) | [https://open-meteo.com/en/docs/historical-weather-api](https://open-meteo.com/en/docs/historical-weather-api) |
| Open-Meteo | Plataforma de datos meteorológicos abiertos | [https://open-meteo.com/](https://open-meteo.com/) |

## Licencia

MIT

---

# Climate Data Lake - Peru

Did you know Peru has 28 of the world's 32 climates according to the Koppen classification? In a single country you can find deserts with no rain for decades, rainforests with 4,000 mm of annual rainfall, and cities at 4,300 meters above sea level where the temperature swings 25°C in a single day.

I'm Gian Cruz. I built this pipeline to capture that climate diversity in a structured data lake. It consumes the Open-Meteo public API for 26 Peruvian cities, stores data in Parquet format partitioned by region and city, and generates metrics for thermal amplitude, climate classification, and extreme event detection across the Coast, Highlands, and Jungle regions.

## Quick start

```bash
git clone https://github.com/giansocial/datalake-clima-peru.git
cd datalake-clima-peru
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
python -m src.pipeline --start 2020-01-01 --end 2023-12-31
```

## Data sources

| Source | Description | Link |
|--------|-------------|------|
| Open-Meteo Archive API | Historical daily climate data (temperature, precipitation, wind) | [https://open-meteo.com/en/docs/historical-weather-api](https://open-meteo.com/en/docs/historical-weather-api) |
| Open-Meteo | Open meteorological data platform | [https://open-meteo.com/](https://open-meteo.com/) |

## License

MIT
