# Megh, Upload Date: 2026-07-28
from app.audio.features import LibrosaFeatureExtractor
from app.ml.artifact_model import ArtifactAcousticClassifier
from app.ml.schemas import AnalysisResponse


class AcousticAnalyzer:
    def __init__(
        self,
        extractor: LibrosaFeatureExtractor | None = None,
        classifier: ArtifactAcousticClassifier | None = None,
    ) -> None:
        self.extractor = extractor or LibrosaFeatureExtractor()
        self.classifier = classifier or ArtifactAcousticClassifier()

    def analyze(self, file_name: str, audio_bytes: bytes) -> AnalysisResponse:
        features = self.extractor.extract(audio_bytes)
        prediction = self.classifier.predict(features)
        return AnalysisResponse(
            file_name=file_name,
            duration_seconds=round(features.duration_seconds, 3),
            decision=prediction.decision,
            confidence=prediction.confidence,
            predicted_class=prediction.predicted_class,
            voice_authenticity=prediction.voice_authenticity,
            background_authenticity=prediction.background_authenticity,
            mismatch_detected=prediction.mismatch_detected,
            class_probabilities=prediction.class_probabilities,
            risk_factors=prediction.risk_factors,
            features=features.to_public_dict(),
            segments=prediction.segments,
            explanation=prediction.explanation,
            model_metadata=prediction.model_metadata,
        )

