import logging
from pathlib import Path
import pandas as pd

log = logging.getLogger(__name__)


def write_partitioned(
    df: pd.DataFrame,
    output_dir: Path,
    partition_cols: list[str],
    name: str = "data",
) -> list[Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    written = []

    if not partition_cols:
        out = output_dir / f"{name}.parquet"
        df.to_parquet(out, index=False, engine="pyarrow")
        written.append(out)
        log.info("escrito %s (%d filas)", out.name, len(df))
        return written

    for keys, group in df.groupby(partition_cols):
        if isinstance(keys, str):
            keys = (keys,)
        parts = "/".join(
            f"{col}={val}" for col, val in zip(partition_cols, keys)
        )
        part_dir = output_dir / parts
        part_dir.mkdir(parents=True, exist_ok=True)
        out = part_dir / f"{name}.parquet"
        group.to_parquet(out, index=False, engine="pyarrow")
        written.append(out)

    log.info("escritas %d particiones en %s", len(written), output_dir)
    return written


def read_lake(lake_dir: Path, filters: dict = None) -> pd.DataFrame:
    parquet_files = list(lake_dir.rglob("*.parquet"))
    if not parquet_files:
        return pd.DataFrame()
    frames = []
    for f in parquet_files:
        df = pd.read_parquet(f, engine="pyarrow")
        if filters:
            for col, val in filters.items():
                if col in df.columns:
                    if isinstance(val, list):
                        df = df[df[col].isin(val)]
                    else:
                        df = df[df[col] == val]
        frames.append(df)
    return pd.concat(frames, ignore_index=True)


def lake_stats(lake_dir: Path) -> dict:
    parquet_files = list(lake_dir.rglob("*.parquet"))
    total_rows = 0
    total_size = 0
    cities = set()
    for f in parquet_files:
        total_size += f.stat().st_size
        df = pd.read_parquet(f, engine="pyarrow")
        total_rows += len(df)
        if "ciudad" in df.columns:
            cities.update(df["ciudad"].unique())
    return {
        "archivos": len(parquet_files),
        "filas_totales": total_rows,
        "tamano_mb": round(total_size / (1024 * 1024), 2),
        "ciudades": sorted(cities),
    }
