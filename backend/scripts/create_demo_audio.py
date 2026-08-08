# Shubhangi, Upload Date: 2026-07-28
# Prepare Demo Audio Files for Analyst Dashboard
from __future__ import annotations

import glob
import os
import shutil
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[1]
DATASET_DIR = BACKEND_ROOT.parent / "dataset-20260722T193837Z-1-001" / "dataset"
DEMO_DIR = BACKEND_ROOT / "data" / "demo_samples"


def main() -> None:
    DEMO_DIR.mkdir(parents=True, exist_ok=True)
    classes = {
        "authentic_speech": ("real_voice_real_bg_wf_2s", "Authentic Speech in Natural Room"),
        "synthetic_voice_real_bg": ("fake_voice_real_bg_wf_2s", "Deepfake Voice in Real Background"),
        "real_voice_fake_bg": ("real_voice_fake_bg_wf_2s", "Real Voice with Injected Room Acoustics"),
        "synthetic_deepfake_full": ("fake_voice_fake_bg_wf_2s", "Full Deepfake (Synthetic Voice + Fake Room)"),
    }

    manifest = []
    for key, (folder, description) in classes.items():
        folder_path = DATASET_DIR / folder
        wavs = sorted(glob.glob(str(folder_path / "**" / "*.wav"), recursive=True))
        if wavs:
            src = wavs[0]
            dst = DEMO_DIR / f"{key}.wav"
            shutil.copy(src, dst)
            print(f"Copied demo sample [{key}] -> {dst.resolve()}")
            manifest.append({
                "id": key,
                "name": description,
                "filename": f"{key}.wav",
                "file_path": str(dst.resolve()),
                "target_class": folder.replace("_wf_2s", "")
            })

    print(f"Prepared {len(manifest)} demo audio samples in {DEMO_DIR.resolve()}")


if __name__ == "__main__":
    main()
