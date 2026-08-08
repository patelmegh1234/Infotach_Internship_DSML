# Fathima, Upload Date: 2026-07-28
# High-Performance Feature Extraction & Model Training Pipeline
from __future__ import annotations

import argparse
import json
import sys
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
from pathlib import Path
from time import perf_counter

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import ExtraTreesClassifier, GradientBoostingClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)
from sklearn.model_selection import StratifiedGroupKFold, StratifiedShuffleSplit
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from app.audio.features import LibrosaFeatureExtractor
from app.audio.vectorizer import FEATURE_NAMES, features_to_vector
from prepare_dataset import build_manifest


def _extract_single_file(path_str: str) -> dict[str, float | str] | None:
    try:
        extractor = LibrosaFeatureExtractor()
        features = extractor.extract_file(path_str)
        vector = features_to_vector(features)
        feature_row = {"path": path_str}
        feature_row.update({name: float(value) for name, value in zip(FEATURE_NAMES, vector, strict=False)})
        return feature_row
    except Exception:
        return None


def main() -> None:
    parser = argparse.ArgumentParser(description="Train AcousticSpace dataset-backed classifiers.")
    parser.add_argument("--dataset-dir", default="../dataset-20260722T193837Z-1-001/dataset")
    parser.add_argument("--output-dir", default="model_artifacts")
    parser.add_argument("--cache", default="data/processed/acoustic_features.csv")
    parser.add_argument("--max-per-class", type=int, default=750)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    cache_path = Path(args.cache)
    cache_path.parent.mkdir(parents=True, exist_ok=True)

    manifest = build_manifest(Path(args.dataset_dir).resolve())
    if args.max_per_class > 0:
        sampled_frames = []
        for _, frame in manifest.groupby("class_name", sort=True):
            sampled_frames.append(frame.sample(n=min(len(frame), args.max_per_class), random_state=args.seed))
        manifest = pd.concat(sampled_frames, ignore_index=True)

    print(f"Loaded manifest with {len(manifest)} files. Extracting acoustic features...")
    features_df = _load_or_extract_features(manifest, cache_path)
    data = manifest.merge(features_df, on="path", how="inner")

    X = data[FEATURE_NAMES].to_numpy(dtype=np.float32)
    y = data["class_name"].to_numpy()
    groups = data["utterance_id"].to_numpy()

    train_idx, test_idx = _grouped_holdout_indices(y=y, groups=groups, seed=args.seed)
    X_train, X_test = X[train_idx], X[test_idx]
    y_train, y_test = y[train_idx], y[test_idx]
    train_groups = groups[train_idx]

    print(f"Dataset Split: {len(X_train)} Train samples, {len(X_test)} Test samples across {len(np.unique(groups))} unique utterances.")

    candidates = {
        "extra_trees": ExtraTreesClassifier(
            n_estimators=300,
            max_depth=25,
            class_weight="balanced",
            random_state=args.seed,
        ),
        "random_forest": RandomForestClassifier(
            n_estimators=300,
            max_depth=22,
            class_weight="balanced",
            random_state=args.seed,
        ),
        "logistic_regression": Pipeline(
            [
                ("scale", StandardScaler()),
                ("model", LogisticRegression(max_iter=2000, class_weight="balanced")),
            ]
        ),
    }

    cv = StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=args.seed)
    comparison: dict[str, dict[str, float]] = {}
    best_name = ""
    best_score = -1.0
    best_model = None

    print("\n--- Starting 5-Fold Stratified Group Cross-Validation ---")
    for name, model in candidates.items():
        start_cv = perf_counter()
        fold_accs = []
        fold_f1s = []

        for train_i, val_i in cv.split(X_train, y_train, train_groups):
            # Fit model clone on fold
            model.fit(X_train[train_i], y_train[train_i])
            val_preds = model.predict(X_train[val_i])
            fold_accs.append(accuracy_score(y_train[val_i], val_preds))
            fold_f1s.append(f1_score(y_train[val_i], val_preds, average="macro"))

        elapsed = perf_counter() - start_cv
        cv_acc = float(np.mean(fold_accs))
        cv_f1 = float(np.mean(fold_f1s))

        comparison[name] = {
            "cv_accuracy_mean": cv_acc,
            "cv_accuracy_std": float(np.std(fold_accs)),
            "cv_balanced_accuracy_mean": cv_acc,
            "cv_f1_macro_mean": cv_f1,
            "cv_seconds": round(elapsed, 2),
        }
        print(f"Model: {name:<20} | CV Acc: {cv_acc:.4f} | CV F1: {cv_f1:.4f} | Time: {elapsed:.2f}s")

        if cv_f1 > best_score:
            best_score = cv_f1
            best_name = name
            best_model = model

    assert best_model is not None
    print(f"\nWinner Model: '{best_name}' with CV F1 score of {best_score:.4f}")

    start_fit = perf_counter()
    best_model.fit(X_train, y_train)
    training_seconds = perf_counter() - start_fit

    y_pred = best_model.predict(X_test)
    labels = sorted(pd.unique(y))

    voice_true = np.array(["fake" if "fake_voice" in label else "real" for label in y_test])
    voice_pred = np.array(["fake" if "fake_voice" in label else "real" for label in y_pred])
    voice_acc = float(accuracy_score(voice_true, voice_pred))

    metrics = {
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "dataset_rows": int(len(data)),
        "train_rows": int(len(train_idx)),
        "test_rows": int(len(test_idx)),
        "feature_count": int(X.shape[1]),
        "max_per_class": int(args.max_per_class),
        "best_model": best_name,
        "holdout_accuracy": float(accuracy_score(y_test, y_pred)),
        "holdout_balanced_accuracy": float(balanced_accuracy_score(y_test, y_pred)),
        "holdout_f1_macro": float(f1_score(y_test, y_pred, average="macro")),
        "holdout_precision_macro": float(precision_score(y_test, y_pred, average="macro")),
        "holdout_recall_macro": float(recall_score(y_test, y_pred, average="macro")),
        "voice_binary_accuracy": voice_acc,
        "training_seconds": round(float(training_seconds), 3),
        "comparison": comparison,
        "classification_report": classification_report(y_test, y_pred, output_dict=True),
        "confusion_matrix": confusion_matrix(y_test, y_pred, labels=labels).tolist(),
        "labels": labels,
    }

    feature_importance = _feature_importance(best_model)
    artifact = {
        "pipeline": best_model,
        "labels": labels,
        "feature_names": FEATURE_NAMES,
        "feature_importance": feature_importance,
        "metadata": {
            "model_type": best_name,
            "trained_at_utc": metrics["created_at_utc"],
            "holdout_accuracy": round(metrics["holdout_accuracy"], 4),
            "holdout_f1_macro": round(metrics["holdout_f1_macro"], 4),
            "voice_binary_accuracy": round(voice_acc, 4),
            "dataset_rows": metrics["dataset_rows"],
            "feature_count": metrics["feature_count"],
            "validation_strategy": "utterance-grouped holdout plus StratifiedGroupKFold",
        },
    }

    joblib.dump(artifact, output_dir / "acousticspace_model.joblib")
    (output_dir / "metrics.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    pd.Series(feature_importance).sort_values(ascending=False).to_csv(output_dir / "feature_importance.csv")
    _write_model_card(output_dir / "MODEL_CARD.md", metrics)

    print("\n--- Final Model Metrics ---")
    print(f"4-Class Holdout Accuracy: {metrics['holdout_accuracy']:.4f}")
    print(f"4-Class Holdout Macro F1: {metrics['holdout_f1_macro']:.4f}")
    print(f"Voice Authentic/Fake Binary Accuracy: {metrics['voice_binary_accuracy']:.4f}")
    print(f"Saved joblib model: {output_dir / 'acousticspace_model.joblib'}")


def _load_or_extract_features(manifest: pd.DataFrame, cache_path: Path) -> pd.DataFrame:
    if cache_path.exists():
        cached = pd.read_csv(cache_path)
        missing_paths = set(manifest["path"]) - set(cached["path"])
        missing_columns = set(FEATURE_NAMES) - set(cached.columns)
        if not missing_paths and not missing_columns:
            return cached[cached["path"].isin(set(manifest["path"]))].reset_index(drop=True)
        print("Rebuilding feature cache with multiprocessing...")

    paths = list(manifest["path"])
    rows = []
    start = perf_counter()

    with ProcessPoolExecutor() as executor:
        for index, result in enumerate(executor.map(_extract_single_file, paths, chunksize=50), start=1):
            if result is not None:
                rows.append(result)
            if index % 500 == 0 or index == len(paths):
                elapsed = perf_counter() - start
                print(f"Parallel Extraction: {index}/{len(paths)} files processed ({index/max(elapsed, 0.001):.1f} files/sec)")

    df = pd.DataFrame(rows)
    df.to_csv(cache_path, index=False)
    print(f"Saved parallel feature cache: {cache_path.resolve()}")
    return df


def _grouped_holdout_indices(y: np.ndarray, groups: np.ndarray, seed: int) -> tuple[np.ndarray, np.ndarray]:
    splitter = StratifiedShuffleSplit(n_splits=1, test_size=0.2, random_state=seed)
    group_df = pd.DataFrame({"group": groups, "label": y}).drop_duplicates("group")
    group_labels = group_df["label"].to_numpy()
    group_values = group_df["group"].to_numpy()
    train_group_idx, test_group_idx = next(splitter.split(group_values, group_labels))
    train_groups = set(group_values[train_group_idx])
    test_groups = set(group_values[test_group_idx])
    train_idx = np.asarray([index for index, group in enumerate(groups) if group in train_groups], dtype=int)
    test_idx = np.asarray([index for index, group in enumerate(groups) if group in test_groups], dtype=int)
    return train_idx, test_idx


def _feature_importance(model) -> dict[str, float]:
    estimator = model.named_steps["model"] if isinstance(model, Pipeline) else model
    if hasattr(estimator, "feature_importances_"):
        values = estimator.feature_importances_
    elif hasattr(estimator, "coef_"):
        values = np.mean(np.abs(estimator.coef_), axis=0)
    else:
        values = np.ones(len(FEATURE_NAMES), dtype=float)
    values = np.asarray(values, dtype=float)
    values = values / (np.sum(values) + 1e-12)
    return {name: float(value) for name, value in zip(FEATURE_NAMES, values, strict=False)}


def _write_model_card(path: Path, metrics: dict) -> None:
    lines = [
        "<!-- Fathima, Upload Date: 2026-07-16 -->",
        "# AcousticSpace Trained Model Card",
        "",
        f"- Best model: `{metrics['best_model']}`",
        f"- 4-Class Holdout Accuracy: `{metrics['holdout_accuracy']:.4f}`",
        f"- 4-Class Holdout Macro F1: `{metrics['holdout_f1_macro']:.4f}`",
        f"- Voice Authenticity Binary Accuracy: `{metrics['voice_binary_accuracy']:.4f}`",
        f"- Validation Strategy: Utterance-grouped holdout plus StratifiedGroupKFold",
        f"- Rows Used: `{metrics['dataset_rows']}` across `{metrics['feature_count']}` features",
        "",
        "## Target Class Map",
        "- `fake_voice_fake_bg`: Synthetic voice with artificial room background.",
        "- `fake_voice_real_bg`: Synthetic voice spliced onto authentic acoustic background.",
        "- `real_voice_fake_bg`: Human speech with inserted or simulated acoustic background.",
        "- `real_voice_real_bg`: Authentic human voice recording in natural acoustic environment.",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    main()
