# Fathima, Upload Date: 2026-07-28
from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from prepare_dataset import build_manifest


def main() -> None:
    parser = argparse.ArgumentParser(description="Run EDA for the AcousticSpace dataset.")
    parser.add_argument("--dataset-dir", default="../dataset-20260722T193837Z-1-001/dataset")
    parser.add_argument("--output-dir", default="reports/eda")
    args = parser.parse_args()

    dataset_dir = Path(args.dataset_dir).resolve()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    manifest = build_manifest(dataset_dir)
    manifest_path = output_dir / "dataset_manifest.csv"
    manifest.to_csv(manifest_path, index=False)

    summary = {
        "total_files": len(manifest),
        "duplicate_paths": int(manifest["path"].duplicated().sum()),
        "duplicate_file_names": int(manifest["file_name"].duplicated().sum()),
        "class_counts": manifest["class_name"].value_counts().to_dict(),
        "mix_profile_counts": manifest["mix_profile"].value_counts().to_dict(),
        "unique_utterances": int(manifest["utterance_id"].nunique()),
        "unique_backgrounds": int(manifest["background_id"].nunique()),
    }
    (output_dir / "eda_summary.json").write_text(pd.Series(summary).to_json(indent=2), encoding="utf-8")

    sns.set_theme(style="whitegrid")
    _barplot(manifest, "class_name", output_dir / "class_distribution.png", "Class distribution")
    _barplot(manifest, "mix_profile", output_dir / "mix_profile_distribution.png", "Mix profile distribution")

    cross = pd.crosstab(manifest["class_name"], manifest["mix_profile"])
    plt.figure(figsize=(9, 5))
    sns.heatmap(cross, annot=True, fmt="d", cmap="Blues")
    plt.title("Class by mix profile")
    plt.tight_layout()
    plt.savefig(output_dir / "class_mix_heatmap.png", dpi=160)
    plt.close()

    markdown = [
        "# AcousticSpace Dataset EDA",
        "",
        f"- Total WAV files: {summary['total_files']}",
        f"- Duplicate paths: {summary['duplicate_paths']}",
        f"- Duplicate file names: {summary['duplicate_file_names']}",
        f"- Unique utterances: {summary['unique_utterances']}",
        f"- Unique backgrounds: {summary['unique_backgrounds']}",
        "",
        "## Class Counts",
        "",
        _series_to_markdown(manifest["class_name"].value_counts()),
        "",
        "## Mix Profile Counts",
        "",
        _series_to_markdown(manifest["mix_profile"].value_counts()),
        "",
        "Leakage control: model validation groups by utterance ID so the same spoken item is not split across train and test.",
    ]
    (output_dir / "EDA_REPORT.md").write_text("\n".join(markdown), encoding="utf-8")
    print(f"EDA saved to {output_dir.resolve()}")


def _barplot(df: pd.DataFrame, column: str, output: Path, title: str) -> None:
    plt.figure(figsize=(10, 5))
    order = df[column].value_counts().index
    ax = sns.countplot(data=df, x=column, order=order, color="#2563eb")
    ax.set_title(title)
    ax.set_xlabel(column.replace("_", " ").title())
    ax.set_ylabel("File count")
    ax.tick_params(axis="x", rotation=20)
    plt.tight_layout()
    plt.savefig(output, dpi=160)
    plt.close()


def _series_to_markdown(series: pd.Series) -> str:
    lines = ["| value | count |", "| --- | ---: |"]
    for value, count in series.items():
        lines.append(f"| {value} | {int(count)} |")
    return "\n".join(lines)


if __name__ == "__main__":
    main()
