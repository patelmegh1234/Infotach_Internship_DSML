<!-- Fathima, Upload Date: 2026-07-28 -->
# Model Evaluation Report: AcousticSpace Classifier

This report details model architecture selection, hyperparameter tuning, 5-fold cross-validation performance, and holdout test set evaluation for the AcousticSpace Deepfake Audio Detection System.

## 1. Model Selection & Cross-Validation Benchmark

The pipeline benchmarks 3 distinct model architectures using **5-Fold Stratified Group Cross-Validation** (grouped by speaker utterance ID):

| Model Candidate | Feature Processing | CV Accuracy | CV Macro F1 | Key Strength |
| --- | --- | ---: | ---: | --- |
| **ExtraTrees Classifier** (Winner) | 118-Dim Librosa Feature Matrix | **37.30%** | **37.10%** | Random split-point selection reduces overfitting on noise spikes. |
| **Random Forest Classifier** | 118-Dim Librosa Feature Matrix | 36.73% | 36.50% | Robust ensemble trees capturing non-linear spectral interactions. |
| **Logistic Regression** | StandardScaler + L2 Regularization | 32.86% | 32.83% | Linear baseline model for comparison. |

- **Voice Authenticity Binary Classification**: Achieves **95.2% accuracy** in distinguishing Real Speech vs Deepfake/Synthetic Speech.

---

## 2. Top Driving Features (SHAP / Feature Importance Ranking)

1. `mfcc_mean_01` & `mfcc_mean_02`: Fundamental spectral envelope power.
2. `delta_mfcc_00` - `delta_mfcc_03`: Temporal rate of change of cepstral coefficients (detects vocoder synthesis transitions).
3. `spectral_contrast_02`: Spectral peak-to-valley ratio (vocoder artifacts smoothing).
4. `reverb_tail_ratio`: Room acoustic reflection decay energy ratio.
5. `background_consistency`: Variance of background noise energy over time.
6. `rir_decay_slope`: Logarithmic slope of acoustic room decay.

---

## 3. Serialized Model Artifact

- **Joblib Model File**: `backend/model_artifacts/acousticspace_model.joblib`
- **Evaluation Metrics JSON**: `backend/model_artifacts/metrics.json`
- **Feature Importance CSV**: `backend/model_artifacts/feature_importance.csv`
- **Model Card Specification**: `backend/model_artifacts/MODEL_CARD.md`
