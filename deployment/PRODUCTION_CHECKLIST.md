<!-- Megh, Upload Date: 2026-07-28 -->
# Production Readiness Checklist & Deployment Guide

This document provides operational verification guidelines, containerization instructions, and cloud deployment procedures for Render, Railway, Vercel, and Docker Compose.

## 1. Operational Checklist

- [x] **Data Preprocessing & EDA**: Manifest constructed for 12,000 WAV files without path duplicates.
- [x] **Feature Vectorizer**: 118-dimensional Librosa acoustic feature extractor verified with zero NaN values.
- [x] **Leakage Prevention**: Utterance-grouped 5-fold cross-validation (`StratifiedGroupKFold`) enforced.
- [x] **Model Artifact**: Serialized joblib model and metrics.json stored in `backend/model_artifacts/`.
- [x] **FastAPI Backend**: Modular endpoints (`/health`, `/api/analyze`, `/api/metrics`, `/api/eda-summary`, `/api/demo-samples`).
- [x] **SaaS Frontend Dashboard**: React + TypeScript interface with Dark/Light theme toggle, live waveform playback, probability distribution bars, and demo audio sample selector.
- [x] **Automated Tests**: Pytest test suite covering feature extraction, classifier inference, and REST API contract.

---

## 2. Docker & Local Deployment

### A. Docker Compose (Single Command)
```bash
docker compose up --build
```
- **Frontend Dashboard**: `http://localhost:5173`
- **FastAPI Backend & API Docs**: `http://localhost:8000/docs`

### B. Manual Backend Execution
```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### C. Manual Frontend Execution
```bash
cd frontend
npm install
npm run dev
```

---

## 3. Cloud Deployment Procedures

### Render / Railway (Backend API)
1. Connect GitHub repository to Render / Railway.
2. Set Root Directory to `backend/`.
3. Build Command: `pip install -r requirements.txt`.
4. Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`.

### Vercel / Netlify (Frontend SaaS App)
1. Connect GitHub repository to Vercel.
2. Set Root Directory to `frontend/`.
3. Set Environment Variable: `VITE_API_BASE_URL=https://your-backend-api.onrender.com`.
4. Deploy!
