# Fathima, Upload Date: 2026-07-28
from __future__ import annotations

from pathlib import Path
from typing import Any

import joblib
import numpy as np

from app.audio.features import AcousticFeatures
from app.audio.vectorizer import FEATURE_NAMES, features_to_vector
from app.ml.model import BaselineAcousticClassifier
from app.ml.schemas import ModelPrediction, SuspiciousSegment

PROJECT_ROOT = Path(__file__).resolve().parents[3]
BACKEND_ROOT = Path(__file__).resolve().parents[2]
CANDIDATE_PATHS = [
    BACKEND_ROOT / "model_artifacts" / "acousticspace_model.joblib",
    PROJECT_ROOT / "model_artifacts" / "acousticspace_model.joblib",
]
DEFAULT_ARTIFACT_PATH = CANDIDATE_PATHS[0]


class ArtifactAcousticClassifier:
    def __init__(self, artifact_path: Path | None = None) -> None:
        self.artifact_path = artifact_path or DEFAULT_ARTIFACT_PATH
        self.fallback = BaselineAcousticClassifier()
        self.artifact: dict[str, Any] | None = None
        self.pipeline = None
        self.labels: list[str] = []
        self.metadata: dict[str, float | int | str] = {}
        self.feature_importance: dict[str, float] = {}
        self._load_artifact()

    @property
    def is_trained(self) -> bool:
        return self.pipeline is not None

    def predict(self, features: AcousticFeatures) -> ModelPrediction:
        if self.pipeline is None:
            prediction = self.fallback.predict(features)
            return prediction.model_copy(update={
                "model_metadata": {
                    "model_type": "baseline_fallback",
                    "artifact_loaded": "false",
                }
            })

        vector = features_to_vector(features).reshape(1, -1)
        probabilities = self.pipeline.predict_proba(vector)[0]
        index = int(np.argmax(probabilities))
        predicted_class = self.labels[index]
        probability_map = {
            label: round(float(probability), 4)
            for label, probability in zip(self.labels, probabilities, strict=False)
        }
        confidence = float(probabilities[index])

        voice_authenticity, background_authenticity = _split_label(predicted_class)
        mismatch_detected = voice_authenticity != background_authenticity
        decision = "likely_real" if predicted_class == "real_voice_real_bg" else "suspicious"
        risk_factors = _risk_factors(
            predicted_class=predicted_class,
            voice_authenticity=voice_authenticity,
            background_authenticity=background_authenticity,
            confidence=confidence,
        )

        # Build feature explanation from trained artifact importance scores
        explanation = self._explain_vector(features_to_vector(features), top_k=12)

        return ModelPrediction(
            decision=decision,
            confidence=round(confidence, 4),
            predicted_class=predicted_class,
            voice_authenticity=voice_authenticity,
            background_authenticity=background_authenticity,
            mismatch_detected=mismatch_detected,
            class_probabilities=probability_map,
            risk_factors=risk_factors,
            segments=self._segments_from_curve(features, decision),
            explanation=explanation,
            model_metadata=self.metadata,
        )

    def _load_artifact(self) -> None:
        target_path = self.artifact_path
        if target_path is None or not target_path.exists():
            for cand in CANDIDATE_PATHS:
                if cand.exists():
                    target_path = cand
                    break
        if target_path is None or not target_path.exists():
            return
        loaded = joblib.load(target_path)
        artifact_features = list(loaded.get("feature_names", []))
        if len(artifact_features) != len(FEATURE_NAMES):
            self.metadata = {
                "model_type": "baseline_fallback",
                "artifact_loaded": "false",
                "fallback_reason": "trained artifact feature schema length does not match current feature extractor",
            }
            return
        self.artifact = loaded
        self.pipeline = loaded["pipeline"]
        self.labels = list(loaded["labels"])
        self.metadata = dict(loaded.get("metadata", {}))
        self.metadata["artifact_loaded"] = "true"
        self.feature_importance = dict(loaded.get("feature_importance", {}))

    def _explain_vector(self, vector: np.ndarray, top_k: int) -> list[dict[str, float | str]]:
        if not self.feature_importance:
            return []
        rows = []
        for name, value in zip(FEATURE_NAMES, vector, strict=False):
            rows.append(
                {
                    "feature": name,
                    "value": round(float(value), 5),
                    "importance": round(float(self.feature_importance.get(name, 0.0)), 6),
                }
            )
        rows.sort(key=lambda row: abs(float(row["importance"])), reverse=True)
        return rows[:top_k]

    @staticmethod
    def _segments_from_curve(features: AcousticFeatures, decision: str) -> list[SuspiciousSegment]:
        curve = np.asarray(features.anomaly_curve, dtype=np.float32)
        if curve.size == 0 or decision == "likely_real":
            return []
        threshold = max(0.64, float(np.quantile(curve, 0.84)))
        frame_duration = features.duration_seconds / max(curve.size, 1)
        segments = []
        for index in np.where(curve >= threshold)[0][:8]:
            start = round(float(index * frame_duration), 2)
            end = round(float(min(features.duration_seconds, start + frame_duration)), 2)
            segments.append(
                SuspiciousSegment(
                    start=start,
                    end=end,
                    score=round(float(curve[index]), 4),
                    reason="High local acoustic anomaly score",
                )
            )
        return segments


def _split_label(label: str) -> tuple[str, str]:
    voice = "fake" if label.startswith("fake_voice") else "real"
    background = "fake" if "fake_bg" in label else "real"
    return voice, background


def _risk_factors(
    predicted_class: str,
    voice_authenticity: str,
    background_authenticity: str,
    confidence: float,
) -> list[str]:
    if predicted_class == "real_voice_real_bg":
        return ["Voice and room background are both predicted real by the trained model."]

    factors = [f"Trained model predicts {predicted_class.replace('_', ' ')}."]
    if voice_authenticity == "fake":
        factors.append("Voice channel shows synthetic-generation evidence.")
    if background_authenticity == "fake":
        factors.append("Background channel shows artificial-room or injected-environment evidence.")
    if voice_authenticity != background_authenticity:
        factors.append("Voice/background authenticity mismatch is present.")
    if confidence < 0.65:
        factors.append("Confidence is moderate; analyst review is recommended before escalation.")
    return factors

