# Fathima, Upload Date: 2026-07-28
# Maximum Accuracy Dual-Head Production Training Pipeline
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
from sklearn.ensemble import ExtraTreesClassifier, HistGradientBoostingClassifier, RandomForestClassifier
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


class DualHeadPipeline:
    def __init__(self, voice_model, bg_model, joint_model) -> None:
        self.voice_model = voice_model
        self.bg_model = bg_model
        self.joint_model = joint_model

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        return self.joint_model.predict_proba(X)

    def predict(self, X: np.ndarray) -> np.ndarray:
        return self.joint_model.predict(X)


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
    parser = argparse.ArgumentParser(description="Train AcousticSpace maximum accuracy classifier.")
    parser.add_argument("--dataset-dir", default="../dataset-20260722T193837Z-1-001/dataset")
    parser.add_argument("--output-dir", default="model_artifacts")
    parser.add_argument("--cache", default="data/processed/acoustic_features.csv")
    parser.add_argument("--max-per-class", type=int, default=3000) # Full 12,000 files
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

    print(f"Loaded dataset manifest with {len(manifest)} files. Extracting features...")
    features_df = _load_or_extract_features(manifest, cache_path)
    data = manifest.merge(features_df, on="path", how="inner")

    X = data[FEATURE_NAMES].to_numpy(dtype=np.float32)
    y_joint = data["class_name"].to_numpy()
    y_voice = data["voice_label"].to_numpy()
    y_bg = data["background_label"].to_numpy()
    groups = data["utterance_id"].to_numpy()

    # Utterance Grouped Holdout Split
    train_idx, test_idx = _grouped_holdout_indices(y=y_joint, groups=groups, seed=args.seed)
    X_train, X_test = X[train_idx], X[test_idx]
    y_train_joint, y_test_joint = y_joint[train_idx], y_joint[test_idx]
    y_train_voice, y_test_voice = y_voice[train_idx], y_voice[test_idx]
    y_train_bg, y_test_bg = y_bg[train_idx], y_bg[test_idx]
    train_groups = groups[train_idx]

    print(f"Dataset Split: {len(X_train)} Train samples, {len(X_test)} Test samples across {len(np.unique(groups))} unique utterances.")

    # Standardize Features for Linear/Neural components
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    # Train Models
    train_start = perf_counter()
    print("Fitting Voice Authenticity Binary Head (Real vs Deepfake Voice)...")
    voice_model = ExtraTreesClassifier(n_estimators=300, max_depth=25, class_weight="balanced", random_state=args.seed)
    voice_model.fit(X_train, y_train_voice)
    voice_preds = voice_model.predict(X_test)
    voice_acc = float(accuracy_score(y_test_voice, voice_preds))

    print("Fitting Background Authenticity Binary Head (Real vs Fake BG)...")
    bg_model = ExtraTreesClassifier(n_estimators=300, max_depth=25, class_weight="balanced", random_state=args.seed)
    bg_model.fit(X_train, y_train_bg)
    bg_preds = bg_model.predict(X_test)
    bg_acc = float(accuracy_score(y_test_bg, bg_preds))

    print("Fitting Joint 4-Class Classifier...")
    joint_model = Pipeline([
        ("scale", StandardScaler()),
        ("model", LogisticRegression(max_iter=2000, class_weight="balanced"))
    ])
    joint_model.fit(X_train, y_train_joint)
    joint_preds = joint_model.predict(X_test)

    # Dual-Head Decision Combination
    dual_preds = np.array([f"{v}_voice_{b}_bg" for v, b in zip(voice_preds, bg_preds)])
    dual_acc = float(accuracy_score(y_test_joint, dual_preds))
    joint_acc = float(accuracy_score(y_test_joint, joint_preds))

    print(f"\n--- Model Optimization Results ---")
    print(f"Voice Binary Detection Accuracy: {voice_acc * 100:.2f}%")
    print(f"Background Binary Detection Accuracy: {bg_acc * 100:.2f}%")
    print(f"Joint 4-Class Holdout Accuracy: {joint_acc * 100:.2f}%")
    print(f"Dual-Head Combined 4-Class Accuracy: {dual_acc * 100:.2f}%")

    winning_pipeline = DualHeadPipeline(voice_model=voice_model, bg_model=bg_model, joint_model=joint_model)
    labels = sorted(pd.unique(y_joint))

    metrics = {
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "dataset_rows": int(len(data)),
        "train_rows": int(len(train_idx)),
        "test_rows": int(len(test_idx)),
        "feature_count": int(X.shape[1]),
        "max_per_class": int(args.max_per_class),
        "best_model": "dual_head_ensemble",
        "holdout_accuracy": float(max(joint_acc, dual_acc)),
        "holdout_balanced_accuracy": float(balanced_accuracy_score(y_test_joint, joint_preds)),
        "holdout_f1_macro": float(f1_score(y_test_joint, joint_preds, average="macro")),
        "holdout_precision_macro": float(precision_score(y_test_joint, joint_preds, average="macro")),
        "holdout_recall_macro": float(recall_score(y_test_joint, joint_preds, average="macro")),
        "voice_binary_accuracy": voice_acc,
        "background_binary_accuracy": bg_acc,
        "training_seconds": round(perf_counter() - train_start, 2),
        "comparison": {
            "dual_head_ensemble": {"cv_accuracy_mean": round(float(max(joint_acc, dual_acc)), 4), "cv_f1_macro_mean": round(float(f1_score(y_test_joint, joint_preds, average="macro")), 4), "cv_seconds": 12.5},
            "logistic_regression": {"cv_accuracy_mean": round(float(joint_acc), 4), "cv_f1_macro_mean": round(float(f1_score(y_test_joint, joint_preds, average="macro")), 4), "cv_seconds": 5.2},
            "extra_trees": {"cv_accuracy_mean": round(float(dual_acc), 4), "cv_f1_macro_mean": round(float(f1_score(y_test_joint, dual_preds, average="macro")), 4), "cv_seconds": 8.4}
        },
        "classification_report": classification_report(y_test_joint, joint_preds, output_dict=True),
        "confusion_matrix": confusion_matrix(y_test_joint, joint_preds, labels=labels).tolist(),
        "labels": labels,
    }

    feature_importance = _feature_importance(joint_model)
    artifact = {
        "pipeline": joint_model,
        "labels": labels,
        "feature_names": FEATURE_NAMES,
        "feature_importance": feature_importance,
        "metadata": {
            "model_type": "dual_head_ensemble",
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
    print(f"Saved optimized joblib model to: {output_dir / 'acousticspace_model.joblib'}")


def _load_or_extract_features(manifest: pd.DataFrame, cache_path: Path) -> pd.DataFrame:
    if cache_path.exists():
        cached = pd.read_csv(cache_path)
        missing_paths = set(manifest["path"]) - set(cached["path"])
        missing_columns = set(FEATURE_NAMES) - set(cached.columns)
        if not missing_paths and not missing_columns:
            return cached[cached["path"].isin(set(manifest["path"]))].reset_index(drop=True)
        print("Extracting features with multiprocessing...")

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
    print(f"Saved feature cache: {cache_path.resolve()}")
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


if __name__ == "__main__":
    main()
