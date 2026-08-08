# Shubhangi, Upload Date: 2026-07-28
from pathlib import Path
import pandas as pd
from backend.scripts.prepare_dataset import build_manifest

def run_data_pipeline(dataset_dir: str, output_manifest: str) -> pd.DataFrame:
    manifest = build_manifest(Path(dataset_dir))
    Path(output_manifest).parent.mkdir(parents=True, exist_ok=True)
    manifest.to_csv(output_manifest, index=False)
    return manifest

if __name__ == "__main__":
    df = run_data_pipeline("../dataset-20260722T193837Z-1-001/dataset", "backend/data/processed/dataset_manifest.csv")
    print(f"Data pipeline complete. Manifest rows: {len(df)}")
