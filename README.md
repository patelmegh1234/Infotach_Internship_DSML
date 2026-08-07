<!-- Megh, Upload Date: 2026-07-14 -->
# AcousticSpace: Industry-Level Deepfake Audio & Acoustic Forensics Platform

[![CI Workflow](https://github.com/patelmegh1234/Infotach_Internship_DSML/actions/workflows/ci.yml/badge.svg)](https://github.com/patelmegh1234/Infotach_Internship_DSML/actions/workflows/ci.yml)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110.0-009688.svg?logo=fastapi)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18.2-61DAFB.svg?logo=react)](https://react.dev)
[![Python](https://img.shields.io/badge/Python-3.11%2B-blue.svg?logo=python)](https://python.org)
[![Docker](https://img.shields.io/badge/Docker-Enabled-2496ED.svg?logo=docker)](https://docker.com)

AcousticSpace is an industry-level, production-grade deepfake audio detection system that focuses on room impulse response (RIR) decay, acoustic reverberation tails, background noise consistency, and synthetic vocoder cepstral artifacts.

Designed for high-accuracy forensic analysis, AcousticSpace evaluates **12,000 standardized 2.0-second 16kHz audio clips** across 4 primary acoustic classes with zero data leakage.

---

## 🌟 Key Features

- **118-Dimensional Acoustic Feature Extractor**: Librosa extraction pipeline capturing 20 MFCCs + Deltas, Spectral Contrast (7 bands), Mel Spectrogram energies (16 bands), Spectral Centroid, Bandwidth, Rolloff, Flatness, Reverb Tail Ratio, and RIR Decay Slope.
- **Utterance-Grouped Leakage-Free Validation**: `StratifiedGroupKFold` split grouped by speaker/utterance ID (`LJ001-0006`) guaranteeing strict train/test isolation.
- **Ensemble Machine Learning Artifact**: Benchmark suite evaluating ExtraTrees, Random Forest, and Logistic Regression with serialized joblib model pipelines and metrics tracking.
- **Modern SaaS Analyst Dashboard**:
  - Dark / Light Mode theme toggle with persistent state.
  - Tabbed interface: **Forensic Scanner**, **Model Evaluation Metrics**, **Dataset EDA Insights**, and **Case History**.
  - Live HTML5 Canvas waveform rendering and audio playback.
  - 1-Click Instant Demo Sample Picker for synthetic voice, real speech, and room acoustic mismatch testing.
  - Class probability distribution bar charts & temporal acoustic anomaly curve timeline.
- **Production FastAPI Service**: High-throughput REST API with input validation, structured logging, CORS middleware, and complete OpenAPI/Swagger documentation.
- **Deployment & CI/CD Ready**: Docker containerization (`docker compose up --build`), GitHub Actions CI, and production deployment checklists for Render/Railway/Vercel.

---

## 📁 Repository Structure

```text
├── backend/                  FastAPI application, feature extractor, ML models, API routes, tests
│   ├── app/
│   │   ├── api/              REST API routes (/health, /api/analyze, /api/metrics, /api/eda-summary)
│   │   ├── audio/            Librosa feature extractor (118-dim) & feature vectorizer
│   │   ├── core/             Settings & environment variables (.env)
│   │   ├── ml/               Artifact model classifier, baseline fallback, schemas, explainability
│   │   ├── services/         AcousticAnalyzer service orchestrator
│   │   └── utils/            File validation & helpers
│   ├── data/                 Demo audio samples & processed feature cache
│   ├── model_artifacts/      joblib model, metrics.json, feature_importance.csv, MODEL_CARD.md
│   ├── reports/              Generated EDA charts, dataset manifest, markdown reports
│   ├── scripts/              Training scripts, dataset prep, EDA runner, demo audio creator
│   └── tests/                Pytest unit and integration test suite
├── frontend/                 React + Vite + TypeScript SaaS Analyst Dashboard
│   ├── src/
│   │   ├── api/              API client methods
│   │   ├── components/       UploadPanel, WaveformPanel, ResultsPanel, AnalyticsPanel, EdaPanel, HistoryPanel
│   │   ├── styles.css        Modern SaaS CSS design system (Dark/Light mode)
│   │   ├── App.tsx           Main application shell & tab navigation
│   │   └── types.ts          TypeScript interfaces
├── models/                   Model artifacts directory
├── notebooks/                Jupyter Notebook 01_eda_and_dataset_analysis.ipynb
├── configs/                  Central configuration files (config.yaml)
├── pipelines/                Data pipeline processing scripts
├── utils/                    System structured logging utilities
├── docs/                     System Architecture, Dataset Analysis, Model Report, API Docs
├── deployment/               Docker Compose, Dockerfiles, Production Readiness Checklist
└── .github/workflows/        GitHub Actions CI workflow
```

---

## 🚀 Quick Start

### 1. Backend Service
```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
Open `http://localhost:8000/docs` to inspect interactive API documentation.

### 2. Frontend SaaS Dashboard
```bash
cd frontend
npm install
npm run dev
```
Open `http://localhost:5173` to launch the dashboard.

### 3. Single-Command Docker Compose
```bash
docker compose up --build
```
- Frontend: `http://localhost:5173`
- Backend API: `http://localhost:8000`

---

## 🧪 Running Automated Tests

```bash
cd backend
.venv\Scripts\python -m pytest
```

---

## 👥 Team Ownership & Project Structure

| Member | Primary Area | Key Deliverables |
| --- | --- | --- |
| Megh | Repository owner, API & Architecture | FastAPI REST server, Docker, CI workflow, test suite, system docs |
| Shubhangi | Audio Signal Processing | Librosa 118-dim feature extraction, MFCC deltas, RIR decay proxies |
| Fathima | Machine Learning Pipeline | Utterance-grouped CV, model benchmarking, metrics, joblib artifact |
| Dimple | Frontend SaaS Dashboard | React UI/UX, Dark/Light mode, tabbed navigation, waveform visualizer |

---

## 📄 Documentation

- [System Architecture](file:///c:/Users/Megh/Desktop/Project%20by%20Codex/docs/ARCHITECTURE.md)
- [Dataset Analysis Report](file:///c:/Users/Megh/Desktop/Project%20by%20Codex/docs/DATASET_ANALYSIS.md)
- [Model Evaluation Report](file:///c:/Users/Megh/Desktop/Project%20by%20Codex/docs/MODEL_REPORT.md)
- [REST API Specification](file:///c:/Users/Megh/Desktop/Project%20by%20Codex/docs/API_DOCUMENTATION.md)
- [Production Readiness Checklist](file:///c:/Users/Megh/Desktop/Project%20by%20Codex/deployment/PRODUCTION_CHECKLIST.md)
