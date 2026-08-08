# Fathima, Upload Date: 2026-07-28
from __future__ import annotations

import numpy as np

from app.audio.features import AcousticFeatures
from app.ml.schemas import ModelPrediction, SuspiciousSegment


class BaselineAcousticClassifier:
    """Interpretable baseline used until AST fine-tuning is ready."""

    def predict(self, features: AcousticFeatures) -> ModelPrediction:
        risk_factors: list[str] = []

        reverb_risk = _scale(features.reverb_tail_ratio, low=0.18, high=0.62)
        decay_risk = _scale(abs(features.rir_decay_slope), low=0.02, high=0.22)
        background_risk = 1.0 - features.background_consistency
        breath_risk = 1.0 - _bell_score(features.breathing_cadence_score, center=0.34, width=0.32)
        centroid_risk = _scale(features.spectral_centroid_mean, low=1800.0, high=5200.0)

        weighted_score = (
            0.30 * reverb_risk
            + 0.22 * decay_risk
            + 0.22 * background_risk
            + 0.16 * breath_risk
            + 0.10 * centroid_risk
        )
        confidence = float(np.clip(weighted_score, 0.03, 0.98))

        if features.reverb_tail_ratio > 0.55:
            risk_factors.append("High reverb tail suggests unnatural room reflection.")
        if abs(features.rir_decay_slope) > 0.18:
            risk_factors.append("RIR decay proxy is unusually steep or unstable.")
        if features.background_consistency < 0.45:
            risk_factors.append("Background energy changes too sharply for a stable room.")
        if breath_risk > 0.65:
            risk_factors.append("Breathing cadence proxy is weakly aligned with speech rhythm.")
        if features.spectral_centroid_mean > 4800:
            risk_factors.append("Spectral centroid is high, which can appear in synthetic artifacts.")

        decision = "suspicious" if confidence >= 0.62 else "likely_real"
        if not risk_factors:
            risk_factors.append("No strong acoustic mismatch found by baseline checks.")
        elif decision == "likely_real":
            risk_factors = [
                "Advisory only: combined evidence stayed below the suspicious threshold.",
                *risk_factors,
            ]

        return ModelPrediction(
            decision=decision,
            confidence=round(confidence, 4),
            predicted_class="baseline_suspicious" if decision == "suspicious" else "baseline_likely_real",
            voice_authenticity=None,
            background_authenticity=None,
            mismatch_detected=False,
            class_probabilities={},
            risk_factors=risk_factors,
            segments=self._segments_from_curve(features),
            explanation=[],
            model_metadata={"model_type": "interpretable_baseline"},
        )

    @staticmethod
    def _segments_from_curve(features: AcousticFeatures) -> list[SuspiciousSegment]:
        curve = np.asarray(features.anomaly_curve, dtype=np.float32)
        if curve.size == 0:
            return []

        threshold = max(0.62, float(np.quantile(curve, 0.82)))
        frame_duration = features.duration_seconds / max(curve.size, 1)
        candidate_indices = np.where(curve >= threshold)[0]
        segments: list[SuspiciousSegment] = []

        for index in candidate_indices[:8]:
            start = round(float(index * frame_duration), 2)
            end = round(float(min(features.duration_seconds, start + frame_duration)), 2)
            segments.append(
                SuspiciousSegment(
                    start=start,
                    end=end,
                    score=round(float(curve[index]), 4),
                    reason="Localized acoustic anomaly",
                )
            )

        return segments


def _scale(value: float, low: float, high: float) -> float:
    if high <= low:
        return 0.0
    return float(np.clip((value - low) / (high - low), 0.0, 1.0))


def _bell_score(value: float, center: float, width: float) -> float:
    distance = abs(value - center)
    return float(np.clip(1.0 - (distance / max(width, 1e-8)), 0.0, 1.0))
