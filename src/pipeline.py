import argparse
import logging
import json
import time
from pathlib import Path

from src.config.settings import CITIES, DATA_RAW, DATA_LAKE, DATA_PROCESSED
from src.config.settings import DEFAULT_START_DATE, DEFAULT_END_DATE
from src.extract.api_client import fetch_city_batch
from src.transform.cleaner import merge_city_data
from src.transform.enricher import (
    add_thermal_amplitude,
    add_monthly_stats,
    add_climate_classification,
    detect_extreme_events,
)
from src.load.parquet_writer import write_partitioned, lake_stats
from src.utils.logger import setup_logging

log = logging.getLogger(__name__)


def save_raw_json(results: dict, output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    for city, data in results.items():
        fname = city.lower().replace(" ", "_") + ".json"
        with open(output_dir / fname, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False)


def run_pipeline(
    cities: dict = None,
    start_date: str = None,
    end_date: str = None,
) -> dict:
    cities = cities or CITIES
    start_date = start_date or DEFAULT_START_DATE
    end_date = end_date or DEFAULT_END_DATE

    t0 = time.time()
    log.info("iniciando pipeline: %d ciudades, %s a %s", len(cities), start_date, end_date)

    raw = fetch_city_batch(cities, start_date, end_date)
    save_raw_json(raw, DATA_RAW)
    log.info("datos crudos guardados en %s", DATA_RAW)

    df = merge_city_data(raw, cities)
    log.info("registros limpios: %d", len(df))

    df = add_thermal_amplitude(df)

    write_partitioned(
        df,
        DATA_LAKE / "daily",
        partition_cols=["region", "ciudad"],
        name="weather",
    )

    monthly = add_monthly_stats(df)
    monthly = add_climate_classification(monthly)
    write_partitioned(
        monthly,
        DATA_LAKE / "monthly",
        partition_cols=["ciudad"],
        name="stats",
    )

    eventos = detect_extreme_events(df)
    if not eventos.empty:
        write_partitioned(
            eventos,
            DATA_LAKE / "events",
            partition_cols=["tipo"],
            name="extreme",
        )
        log.info("eventos extremos detectados: %d", len(eventos))

    monthly.to_csv(DATA_PROCESSED / "resumen_mensual.csv", index=False)
    if not eventos.empty:
        eventos.to_csv(DATA_PROCESSED / "eventos_extremos.csv", index=False)

    stats = lake_stats(DATA_LAKE)
    elapsed = round(time.time() - t0, 1)
    log.info("pipeline completado en %.1fs", elapsed)
    log.info("lake: %d archivos, %d filas, %.2f MB",
             stats["archivos"], stats["filas_totales"], stats["tamano_mb"])

    return {
        "registros_diarios": len(df),
        "registros_mensuales": len(monthly),
        "eventos_extremos": len(eventos),
        "num_ciudades": len(cities),
        "duracion_seg": elapsed,
        **stats,
    }


def main():
    parser = argparse.ArgumentParser(description="Data lake climatico - Peru")
    parser.add_argument("--start", default=DEFAULT_START_DATE, help="fecha inicio YYYY-MM-DD")
    parser.add_argument("--end", default=DEFAULT_END_DATE, help="fecha fin YYYY-MM-DD")
    parser.add_argument("--cities", nargs="+", help="ciudades especificas")
    args = parser.parse_args()

    setup_logging()

    if args.cities:
        selected = {c: CITIES[c] for c in args.cities if c in CITIES}
        missing = [c for c in args.cities if c not in CITIES]
        if missing:
            log.warning("ciudades no encontradas: %s", missing)
    else:
        selected = CITIES

    result = run_pipeline(selected, args.start, args.end)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
