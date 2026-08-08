# Fathima, Upload Date: 2026-07-28
from app.audio.features import AcousticFeatures
from app.ml.model import BaselineAcousticClassifier


def test_baseline_classifier_returns_valid_prediction() -> None:
    features = AcousticFeatures(
        sample_rate=16000,
        duration_seconds=3.0,
        rms_mean=0.08,
        rms_std=0.04,
        zero_crossing_rate=0.12,
        zero_crossing_rate_std=0.03,
        spectral_centroid_mean=5200.0,
        spectral_centroid_std=900.0,
        spectral_rolloff_mean=7000.0,
        spectral_rolloff_std=1200.0,
        spectral_flatness_mean=0.22,
        spectral_flatness_std=0.05,
        low_frequency_ratio=0.18,
        high_frequency_ratio=0.31,
        mfcc_mean=[0.0] * 20,
        mel_spectrogram_preview=[-20.0] * 16,
        spectral_band_std=[0.1] * 16,
        reverb_tail_ratio=0.7,
        rir_decay_slope=-0.24,
        background_consistency=0.35,
        breathing_cadence_score=0.05,
        anomaly_curve=[0.1, 0.7, 0.8, 0.3],
    )

    prediction = BaselineAcousticClassifier().predict(features)

    assert prediction.decision == "suspicious"
    assert 0 <= prediction.confidence <= 1
    assert prediction.risk_factors
    assert prediction.segments
