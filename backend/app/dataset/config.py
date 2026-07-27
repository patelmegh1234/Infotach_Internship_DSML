from pathlib import Path

# Project root directory
PROJECT_ROOT = Path(__file__).resolve().parents[3]

# Dataset folders
RAW_DATA_PATH = PROJECT_ROOT / "backend" / "data" / "raw"
PROCESSED_DATA_PATH = PROJECT_ROOT / "backend" / "data" / "processed"
METADATA_PATH = PROJECT_ROOT / "backend" / "data" / "metadata"
FEATURE_PATH = PROJECT_ROOT / "backend" / "data" / "features"
SPLITS_PATH = PROJECT_ROOT / "backend" / "data" / "splits"

# Create folders if they don't exist
PROCESSED_DATA_PATH.mkdir(parents=True, exist_ok=True)
METADATA_PATH.mkdir(parents=True, exist_ok=True)
FEATURE_PATH.mkdir(parents=True, exist_ok=True)
SPLITS_PATH.mkdir(parents=True, exist_ok=True)