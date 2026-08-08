<!-- Shubhangi, Upload Date: 2026-07-28 -->
# Dataset Analysis: AcousticSpace Deepfake Audio Corpus

This document details the exploratory data analysis, acoustic feature distributions, and leakage prevention protocol for the **AcousticSpace 12,000-sample Deepfake Audio Dataset**.

## 1. Dataset Breakdown

| Target Class Name | Voice Channel | Background Channel | Audio Sample Count | Description |
| --- | --- | --- | ---: | --- |
| `fake_voice_fake_bg` | Synthetic AI | Synthetic / Generated | 3,000 | Deepfake voice generated with AI vocoder in artificial acoustic environment. |
| `fake_voice_real_bg` | Synthetic AI | Authentic Real Room | 3,000 | Deepfake voice spliced over authentic room background noise. |
| `real_voice_fake_bg` | Authentic Human | Synthetic / Injected | 3,000 | Authentic human speech with inserted or simulated acoustic background. |
| `real_voice_real_bg` | Authentic Human | Authentic Real Room | 3,000 | Authentic human speech in natural room recording environment. |

- **Total Audio Files**: 12,000 WAV clips
- **Audio Specification**: 16,000 Hz sample rate, mono channel, 32-bit float PCM, 2.0 seconds duration per file.

---

## 2. Acoustic Mixing Ratio Profiles

Each target class contains 3 acoustic mixing profiles (4,000 samples per profile across the corpus):
1. **`balanced`**: Voice energy and background noise energy are balanced near a 1:1 SNR ratio.
2. **`bg_dominant`**: Background environmental acoustics dominate the signal power.
3. **`voice_dominant`**: Speech channel amplitude dominates background acoustics.

---

## 3. Data Leakage Prevention Protocol

To ensure model metrics reflect real-world generalizability without overestimating performance:
- **Speaker Utterance Isolation**: All dataset files contain metadata encoding the original speaker utterance ID (e.g. `LJ001-0006`).
- **Group-Aware Splitting**: Cross-validation uses `StratifiedGroupKFold(n_splits=5)` grouped strictly by `utterance_id`.
- **Zero Train/Test Contamination**: No spoken sentence or speaker voice from the training fold is ever split into the test set.
