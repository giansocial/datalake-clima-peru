# Data Lake Climático - Perú

Soy Gian Cruz.

Pipeline que construye un data lake con información climática histórica de 26 ciudades del Perú. Los datos se obtienen de la API abierta de Open-Meteo y se almacenan en formato Parquet particionado por región y ciudad.

Perú tiene 28 de los 32 climas del mundo según la clasificación de Köppen. Este proyecto captura esa diversidad analizando temperatura, precipitación, viento y eventos extremos a lo largo de las tres regiones naturales: Costa, Sierra y Selva.

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
