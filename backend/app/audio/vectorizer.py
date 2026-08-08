# Shubhangi, Upload Date: 2026-07-28
# Acoustic Feature Vectorizer
from __future__ import annotations

from collections.abc import Mapping

import numpy as np

from app.audio.features import AcousticFeatures

BASE_FEATURE_NAMES = [
    "duration_seconds",
    "rms_mean",
    "rms_std",
    "zero_crossing_rate",
    "zero_crossing_rate_std",
    "spectral_centroid_mean",
    "spectral_centroid_std",
    "spectral_rolloff_mean",
    "spectral_rolloff_std",
    "spectral_bandwidth_mean",
    "spectral_bandwidth_std",
    "spectral_flatness_mean",
    "spectral_flatness_std",
    "low_frequency_ratio",
    "high_frequency_ratio",
    "reverb_tail_ratio",
    "rir_decay_slope",
    "background_consistency",
    "breathing_cadence_score",
]

MFCC_MEAN_NAMES = [f"mfcc_mean_{index:02d}" for index in range(20)]
MFCC_STD_NAMES = [f"mfcc_std_{index:02d}" for index in range(20)]
DELTA_MFCC_NAMES = [f"delta_mfcc_{index:02d}" for index in range(20)]
CONTRAST_NAMES = [f"spectral_contrast_{index:02d}" for index in range(7)]
BAND_FEATURE_NAMES = [f"spectral_band_{index:02d}" for index in range(16)]
BAND_STD_FEATURE_NAMES = [f"spectral_band_std_{index:02d}" for index in range(16)]

FEATURE_NAMES = (
    BASE_FEATURE_NAMES
    + MFCC_MEAN_NAMES
    + MFCC_STD_NAMES
    + DELTA_MFCC_NAMES
    + CONTRAST_NAMES
    + BAND_FEATURE_NAMES
    + BAND_STD_FEATURE_NAMES
)


def features_to_vector(features: AcousticFeatures) -> np.ndarray:
    values: list[float] = [
        features.duration_seconds,
        features.rms_mean,
        features.rms_std,
        features.zero_crossing_rate,
        features.zero_crossing_rate_std,
        features.spectral_centroid_mean,
        features.spectral_centroid_std,
        features.spectral_rolloff_mean,
        features.spectral_rolloff_std,
        features.spectral_bandwidth_mean,
        features.spectral_bandwidth_std,
        features.spectral_flatness_mean,
        features.spectral_flatness_std,
        features.low_frequency_ratio,
        features.high_frequency_ratio,
        features.reverb_tail_ratio,
        features.rir_decay_slope,
        features.background_consistency,
        features.breathing_cadence_score,
    ]
    values.extend(_pad(features.mfcc_mean, size=len(MFCC_MEAN_NAMES)))
    values.extend(_pad(features.mfcc_std, size=len(MFCC_STD_NAMES)))
    values.extend(_pad(features.delta_mfcc_mean, size=len(DELTA_MFCC_NAMES)))
    values.extend(_pad(features.spectral_contrast_mean, size=len(CONTRAST_NAMES)))
    values.extend(_pad(features.mel_spectrogram_preview, size=len(BAND_FEATURE_NAMES)))
    values.extend(_pad(features.spectral_band_std, size=len(BAND_STD_FEATURE_NAMES)))
    return np.asarray(values, dtype=np.float32)


def public_features_to_vector(features: Mapping[str, object]) -> np.ndarray:
    values: list[float] = []
    for name in BASE_FEATURE_NAMES:
        values.append(float(features.get(name, 0.0)))
    values.extend(_pad(features.get("mfcc_mean", []), size=len(MFCC_MEAN_NAMES)))
    values.extend(_pad(features.get("mfcc_std", []), size=len(MFCC_STD_NAMES)))
    values.extend(_pad(features.get("delta_mfcc_mean", []), size=len(DELTA_MFCC_NAMES)))
    values.extend(_pad(features.get("spectral_contrast_mean", []), size=len(CONTRAST_NAMES)))
    values.extend(_pad(features.get("mel_spectrogram_preview", []), size=len(BAND_FEATURE_NAMES)))
    values.extend(_pad(features.get("spectral_band_std", []), size=len(BAND_STD_FEATURE_NAMES)))
    return np.asarray(values, dtype=np.float32)


def vector_to_dict(vector: np.ndarray) -> dict[str, float]:
    return {name: float(value) for name, value in zip(FEATURE_NAMES, vector, strict=False)}


def _pad(values: object, size: int) -> list[float]:
    if not isinstance(values, list | tuple | np.ndarray):
        values = []
    clean = [float(value) for value in list(values)[:size]]
    if len(clean) < size:
        clean.extend([0.0] * (size - len(clean)))
    return clean
