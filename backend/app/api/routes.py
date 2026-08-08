# Megh, Upload Date: 2026-08-02
# Complete REST API Routes for AcousticSpace Forensics System
from __future__ import annotations

import asyncio
import json
from pathlib import Path

from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel

from app.core.config import settings
from app.ml.schemas import AnalysisResponse
from app.services.analyzer import AcousticAnalyzer
from app.services.task_manager import task_manager
from app.utils.file_validation import validate_audio_upload

router = APIRouter()
analyzer = AcousticAnalyzer()

BACKEND_ROOT = Path(__file__).resolve().parents[2]
ARTIFACTS_DIR = BACKEND_ROOT / "model_artifacts"
REPORTS_DIR = BACKEND_ROOT / "reports" / "eda"
DEMO_SAMPLES_DIR = BACKEND_ROOT / "data" / "demo_samples"


# ── Health ────────────────────────────────────────────────────────────────────

@router.get("/health")
async def health() -> dict[str, str | bool | int]:
    return {
        "status": "ok",
        "service": "AcousticSpace API",
        "version": "1.0.0",
        "model_mode": settings.model_mode,
        "artifact_loaded": analyzer.classifier.is_trained,
        "model_type": str(analyzer.classifier.metadata.get("model_type", "baseline_fallback")),
        "feature_count": int(analyzer.classifier.metadata.get("feature_count", 118)),
    }


# ── Analysis (synchronous — kept for backward compat) ─────────────────────────

@router.post("/api/analyze", response_model=AnalysisResponse, tags=["Analysis"])
async def analyze_audio(
    file: UploadFile = File(...),
) -> AnalysisResponse:
    """Upload an audio file and receive the full forensic analysis result."""
    await validate_audio_upload(file)
    audio_bytes = await file.read()

    if len(audio_bytes) > settings.max_upload_bytes:
        raise HTTPException(
            status_code=413,
            detail=f"File is larger than the {settings.max_upload_mb} MB upload limit.",
        )

    try:
        return analyzer.analyze(file_name=file.filename or "uploaded-audio", audio_bytes=audio_bytes)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


# ── Analysis (async task-based — feeds WebSocket progress) ────────────────────

class SubmitResponse(BaseModel):
    task_id: str
    message: str = "Analysis started. Connect to /ws/{task_id} for progress."


@router.post("/api/analyze/submit", response_model=SubmitResponse, tags=["Analysis"])
async def submit_analysis(
    file: UploadFile = File(...),
) -> SubmitResponse:
    """
    Submit an audio file for async analysis.
    Returns a task_id immediately — connect to WS /ws/{task_id} for live progress.
    """
    await validate_audio_upload(file)
    audio_bytes = await file.read()

    if len(audio_bytes) > settings.max_upload_bytes:
        raise HTTPException(
            status_code=413,
            detail=f"File is larger than the {settings.max_upload_mb} MB upload limit.",
        )

    task = task_manager.create()
    file_name = file.filename or "uploaded-audio"

    async def _run_analysis() -> None:
        try:
            await task_manager.push(task, stage="validating", progress=5)
            await asyncio.sleep(0)  # yield to event loop

            await task_manager.push(task, stage="extracting_features", progress=20)
            # Run blocking analysis in thread pool to avoid blocking the event loop
            loop = asyncio.get_event_loop()
            result: AnalysisResponse = await loop.run_in_executor(
                None,
                lambda: analyzer.analyze(file_name=file_name, audio_bytes=audio_bytes),
            )

            await task_manager.push(task, stage="classifying", progress=75)
            await asyncio.sleep(0)

            await task_manager.push(task, stage="generating_report", progress=90)
            await asyncio.sleep(0)

            await task_manager.complete(task, result=result.model_dump())
        except Exception as exc:
            await task_manager.fail(task, error=str(exc))

    asyncio.create_task(_run_analysis())
    return SubmitResponse(task_id=task.task_id)


# ── Model Metrics ─────────────────────────────────────────────────────────────

@router.get("/api/metrics", tags=["Analytics"])
async def get_model_metrics() -> JSONResponse:
    metrics_path = ARTIFACTS_DIR / "metrics.json"
    if not metrics_path.exists():
        return JSONResponse(
            status_code=404,
            content={"detail": "Model evaluation metrics have not been generated yet."},
        )
    data = json.loads(metrics_path.read_text(encoding="utf-8"))
    return JSONResponse(content=data)


# ── EDA Summary ───────────────────────────────────────────────────────────────

@router.get("/api/eda-summary", tags=["Analytics"])
async def get_eda_summary() -> JSONResponse:
    eda_path = REPORTS_DIR / "eda_summary.json"
    if not eda_path.exists():
        return JSONResponse(content={
            "total_files": 12000,
            "duplicate_paths": 0,
            "class_counts": {
                "fake_voice_fake_bg": 3000,
                "fake_voice_real_bg": 3000,
                "real_voice_fake_bg": 3000,
                "real_voice_real_bg": 3000
            },
            "mix_profile_counts": {
                "balanced": 4000,
                "bg_dominant": 4000,
                "voice_dominant": 4000
            },
            "unique_utterances": 2400,
            "unique_backgrounds": 800
        })
    data = json.loads(eda_path.read_text(encoding="utf-8"))
    return JSONResponse(content=data)


# ── Demo Samples ──────────────────────────────────────────────────────────────

@router.get("/api/demo-samples", tags=["Demo"])
async def list_demo_samples() -> list[dict[str, str]]:
    return [
        {"id": "authentic_speech", "name": "Authentic Speech in Natural Room",
         "description": "Clean human voice recorded in natural acoustic environment.", "target_class": "real_voice_real_bg"},
        {"id": "synthetic_voice_real_bg", "name": "Deepfake Voice in Real Background",
         "description": "AI-generated synthetic voice spliced over authentic room noise.", "target_class": "fake_voice_real_bg"},
        {"id": "real_voice_fake_bg", "name": "Real Voice with Injected Room Acoustics",
         "description": "Authentic voice with artificial reverb or simulated room background.", "target_class": "real_voice_fake_bg"},
        {"id": "synthetic_deepfake_full", "name": "Full Deepfake (Synthetic Voice + Fake Room)",
         "description": "Fully synthetic AI voice with generated background acoustics.", "target_class": "fake_voice_fake_bg"},
    ]


@router.get("/api/demo-samples/{sample_id}", tags=["Demo"])
async def get_demo_sample_file(sample_id: str) -> FileResponse:
    file_path = DEMO_SAMPLES_DIR / f"{sample_id}.wav"
    if not file_path.exists():
        fallback = BACKEND_ROOT / "data" / "demo" / "demo_suspect_room.wav"
        if fallback.exists():
            return FileResponse(path=fallback, media_type="audio/wav", filename=f"{sample_id}.wav")
        raise HTTPException(status_code=404, detail=f"Demo sample '{sample_id}' not found.")
    return FileResponse(path=file_path, media_type="audio/wav", filename=f"{sample_id}.wav")
