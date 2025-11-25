from pathlib import Path
import pandas as pd

HVV_DATA = "data/HVV"


def load_gtfs_tables(gtfs_dir: str | Path) -> dict[str, pd.DataFrame]:
    """
    Load essential GTFS tables from a directory containing unzipped GTFS files.

    Expected files:
        - stops.txt
        - routes.txt
        - trips.txt
        - stop_times.txt
    """
    gtfs_dir = Path(gtfs_dir)
    tables = {}
    for name in ["stops", "routes", "trips", "stop_times"]:
        path = gtfs_dir / f"{name}.txt"
        if not path.exists():
            raise FileNotFoundError(f"Required GTFS file not found: {path}")
        tables[name] = pd.read_csv(path, low_memory=False)
    return tables
