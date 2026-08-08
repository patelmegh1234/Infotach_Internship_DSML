# Fathima, Upload Date: 2026-07-28
from pydantic import BaseModel, Field


class SuspiciousSegment(BaseModel):
    start: float = Field(..., ge=0)
    end: float = Field(..., ge=0)
    score: float = Field(..., ge=0, le=1)
    reason: str


class AnalysisResponse(BaseModel):
    file_name: str
    duration_seconds: float
    decision: str
    confidence: float = Field(..., ge=0, le=1)
    predicted_class: str | None = None
    voice_authenticity: str | None = None
    background_authenticity: str | None = None
    mismatch_detected: bool = False
    class_probabilities: dict[str, float] = Field(default_factory=dict)
    risk_factors: list[str]
    features: dict[str, float | int | list[float]]
    segments: list[SuspiciousSegment]
    explanation: list[dict[str, float | str]] = Field(default_factory=list)
    model_metadata: dict[str, float | int | str] = Field(default_factory=dict)


class ModelPrediction(BaseModel):
    decision: str
    confidence: float = Field(..., ge=0, le=1)
    predicted_class: str | None = None
    voice_authenticity: str | None = None
    background_authenticity: str | None = None
    mismatch_detected: bool = False
    class_probabilities: dict[str, float] = Field(default_factory=dict)
    risk_factors: list[str]
    segments: list[SuspiciousSegment]
    explanation: list[dict[str, float | str]] = Field(default_factory=list)
    model_metadata: dict[str, float | int | str] = Field(default_factory=dict)

