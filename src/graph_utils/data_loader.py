from pathlib import Path
import pandas as pd
import zipfile

HVV_DATA = "data/HVV"


def _extract_data_if_needed(gtfs_dir: Path):
    """
    Extract GTFS data from archive if files don't exist.
    """
    archive_path = Path("data/HVV_data.zip")
    required_files = ["stops.txt", "routes.txt", "trips.txt", "stop_times.txt"]
    
    # Check if all required files exist
    all_exist = all((gtfs_dir / f).exists() for f in required_files)
    
    if not all_exist and archive_path.exists():
        print("📦 Extracting GTFS data from archive...")
        gtfs_dir.mkdir(parents=True, exist_ok=True)
        try:
            with zipfile.ZipFile(archive_path, 'r') as zip_ref:
                zip_ref.extractall(gtfs_dir)
            print("✓ Data extracted successfully")
        except Exception as e:
            raise RuntimeError(f"Failed to extract data from archive: {e}")


def load_gtfs_tables(gtfs_dir: str | Path) -> dict[str, pd.DataFrame]:
    """
    Load essential GTFS tables from a directory containing unzipped GTFS files.
    Automatically extracts data from archive if files don't exist.

    Expected files:
        - stops.txt
        - routes.txt
        - trips.txt
        - stop_times.txt
    """
    gtfs_dir = Path(gtfs_dir)
    
    # Extract data from archive if needed
    _extract_data_if_needed(gtfs_dir)
    
    tables = {}
    for name in ["stops", "routes", "trips", "stop_times"]:
        path = gtfs_dir / f"{name}.txt"
        if not path.exists():
            raise FileNotFoundError(f"Required GTFS file not found: {path}")
        tables[name] = pd.read_csv(path, low_memory=False)
    return tables
