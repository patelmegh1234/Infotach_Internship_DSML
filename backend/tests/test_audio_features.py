# Shubhangi, Upload Date: 2026-07-28
# Audio Feature Extraction & Vectorization Unit Tests
import numpy as np

from app.audio.features import LibrosaFeatureExtractor
from app.audio.vectorizer import FEATURE_NAMES, features_to_vector


def test_feature_extractor_returns_valid_vector() -> None:
    extractor = LibrosaFeatureExtractor(target_sample_rate=16000)
    sample_rate = 16000
    duration = 2.0
    time = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    # Generate synthetic 180Hz sine wave + noise
    audio = (0.3 * np.sin(2 * np.pi * 180 * time) + 0.05 * np.random.randn(time.size)).astype(np.float32)

    features = extractor.extract_waveform(waveform=audio, sample_rate=sample_rate)

    assert features.sample_rate == 16000
    assert abs(features.duration_seconds - 2.0) < 0.05
    assert features.rms_mean > 0
    assert len(features.mfcc_mean) == 20
    assert len(features.mel_spectrogram_preview) == 16

    vector = features_to_vector(features)
    assert vector.ndim == 1
    assert vector.shape[0] == len(FEATURE_NAMES)
    assert not np.isnan(vector).any()
