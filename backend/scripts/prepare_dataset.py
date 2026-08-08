# Fathima, Upload Date: 2026-07-28
from __future__ import annotations

import argparse
import re
from pathlib import Path

import pandas as pd

LABEL_PATTERN = re.compile(r"^(fake|real)_voice_(fake|real)_bg")


def build_manifest(dataset_dir: Path) -> pd.DataFrame:
    rows: list[dict[str, str | int]] = []
    for path in sorted(dataset_dir.rglob("*.wav")):
        relative = path.relative_to(dataset_dir)
        class_name = relative.parts[0]
        mix_profile = relative.parts[1] if len(relative.parts) > 2 else "unknown"
        match = LABEL_PATTERN.match(class_name)
        if match is None:
            continue
        voice_label, background_label = match.groups()
        filename = path.name
        utterance_id = _utterance_id(filename)
        background_id = _background_id(filename)
        rows.append(
            {
                "path": str(path),
                "relative_path": str(relative).replace("\\", "/"),
                "file_name": filename,
                "class_name": class_name.replace("_wf_2s", ""),
                "voice_label": voice_label,
                "background_label": background_label,
                "is_suspicious": int(class_name != "real_voice_real_bg_wf_2s"),
                "mix_profile": mix_profile,
                "utterance_id": utterance_id,
                "background_id": background_id,
            }
        )
    if not rows:
        raise SystemExit(f"No WAV files found under {dataset_dir}")
    return pd.DataFrame(rows)


def _utterance_id(filename: str) -> str:
    stem = Path(filename).stem
    left = stem.split("__X__")[0]
    return left.replace("_generated", "")


def _background_id(filename: str) -> str:
    stem = Path(filename).stem
    if "__X__" not in stem:
        return "unknown"
    return stem.split("__X__", maxsplit=1)[1].rsplit("_", maxsplit=1)[0]


def main() -> None:
    parser = argparse.ArgumentParser(description="Create a leakage-aware AcousticSpace dataset manifest.")
    parser.add_argument(
        "--dataset-dir",
        default="../dataset-20260722T193837Z-1-001/dataset",
        help="Path to the folder containing fake/real voice-background class folders.",
    )
    parser.add_argument("--output", default="data/processed/dataset_manifest.csv")
    args = parser.parse_args()

    dataset_dir = Path(args.dataset_dir).resolve()
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    manifest = build_manifest(dataset_dir)
    manifest.to_csv(output, index=False)
    print(f"Manifest rows: {len(manifest)}")
    print(manifest.groupby(["class_name", "mix_profile"]).size())
    print(f"Saved: {output.resolve()}")


if __name__ == "__main__":
    main()

