<!-- Shubhangi, Upload Date: 2026-07-28 -->
# System Architecture: AcousticSpace Audio Forensics Platform

AcousticSpace is an industry-level, production-grade Deepfake Audio & Acoustic Mismatch Detection System engineered to analyze synthetic voice artifacts, artificial room impulse response (RIR) decays, and voice-environment mismatches.

```mermaid
graph TD
    User["Analyst / Frontend UI (React + TypeScript)"] -->|Audio File / Demo Sample| API["FastAPI REST Backend"]
    API -->|Validation & File Upload| Validator["File Validator & Stream Reader"]
    Validator -->|Waveform Buffer (16kHz Mono)| Extractor["Librosa Acoustic Feature Extractor"]
    Extractor -->|118-Dim Acoustic Features| Vectorizer["Acoustic Feature Vectorizer"]
    Vectorizer -->|Normalized Feature Vector| Classifier["Artifact Ensemble Classifier (ExtraTrees / RandomForest)"]
    Classifier -->|Predicted Class & Probabilities| Analyzer["Acoustic Analyzer Engine"]
    Extractor -->|RMS & Centroid Profiles| Analyzer
    Analyzer -->|Temporal Anomaly Curve| Segmenter["Suspicious Segment Localizer"]
    Analyzer -->|SHAP Feature Importances| Explainer["Feature Explainability Module"]
    Analyzer -->|AnalysisResponse JSON| User
```

---

## 1. Core Architectural Components

### A. Librosa Acoustic Feature Extractor (`backend/app/audio/features.py`)
- Standardizes incoming audio to 16,000 Hz 32-bit float mono PCM.
- Extracts a **118-dimensional acoustic representation**:
  - **MFCCs (20 coefficients)**: Mean, Std, and Delta MFCCs for spectral envelope & timbre analysis.
  - **Spectral Contrast (7 frequency bands)**: Distinguishes synthetic vocoder spectral smoothing from natural speech peaks.
  - **Mel Spectrogram Energies (16 mel bands)**: Spectral power distribution & band variances.
  - **Spectral Dynamics**: Centroid, Bandwidth, Rolloff, and Flatness.
  - **Room Acoustic Impulse Proxies**: Reverb tail ratio, RIR decay slope, Background energy consistency, Breathing cadence score.

### B. Machine Learning Ensemble Pipeline (`backend/app/ml/artifact_model.py`)
- **Trained Model Artifact**: `acousticspace_model.joblib` containing the winning ExtraTrees / Random Forest classifier.
- **Utterance-Grouped Cross-Validation**: `StratifiedGroupKFold` split grouped strictly by speaker/utterance ID (`LJ001-0006`) to ensure **zero data leakage**.
- **Model Card & Metrics**: Serialized performance metrics in `backend/model_artifacts/metrics.json`.

### C. FastAPI Service Layer (`backend/app/api/routes.py`)
- High-throughput asynchronous REST API providing:
  - `POST /api/analyze`: Multi-part audio upload & forensic analysis.
  - `GET /api/metrics`: Live model performance, confusion matrix, feature importances.
  - `GET /api/eda-summary`: Pre-calculated dataset summary statistics.
  - `GET /api/demo-samples`: Available test audio files for 1-click reviewer testing.

### D. React + Vite Analyst Dashboard (`frontend/src/`)
- Modern SaaS application UI with Dark/Light mode theme toggle.
- Tabbed layout: Forensic Scanner, Model Evaluation Metrics, Dataset EDA Insights, Analyst History.
- Live waveform visualizer, HTML5 audio playback, interactive probability distribution bars, temporal anomaly timeline, and feature explainability tables.
