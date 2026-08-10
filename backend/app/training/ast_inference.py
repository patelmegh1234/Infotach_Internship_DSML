from pathlib import Path

import librosa
import torch
from transformers import (
    AutoFeatureExtractor,
    ASTForAudioClassification,
)


PROJECT_ROOT = Path(__file__).resolve().parents[3]

MODEL_DIR = (
    PROJECT_ROOT
    / "backend"
    / "models"
    / "best_ast_model"
)

SAMPLE_RATE = 16000

LABELS = {
    0: "fake",
    1: "real",
}


class ASTDeepfakeClassifier:

    def __init__(
        self,
        model_dir=MODEL_DIR
    ):

        self.model_dir = Path(model_dir)

        if not self.model_dir.exists():
            raise FileNotFoundError(
                f"AST model directory not found: "
                f"{self.model_dir}"
            )

        self.device = torch.device(
            "cuda"
            if torch.cuda.is_available()
            else "cpu"
        )

        self.feature_extractor = (
            AutoFeatureExtractor.from_pretrained(
                str(self.model_dir),
                local_files_only=True
            )
        )

        self.model = (
            ASTForAudioClassification
            .from_pretrained(
                str(self.model_dir),
                local_files_only=True
            )
        )

        self.model.to(
            self.device
        )

        self.model.eval()

        print(
            f"AST model loaded on: "
            f"{self.device}"
        )

    def preprocess_audio(
        self,
        audio_path
    ):

        audio_path = Path(audio_path)

        if not audio_path.exists():
            raise FileNotFoundError(
                f"Audio file not found: "
                f"{audio_path}"
            )

        audio, _ = librosa.load(
            audio_path,
            sr=SAMPLE_RATE,
            mono=True
        )

        inputs = (
            self.feature_extractor(
                audio,
                sampling_rate=SAMPLE_RATE,
                return_tensors="pt"
            )
        )

        return {
            key: value.to(self.device)
            for key, value
            in inputs.items()
        }

    def predict(
        self,
        audio_path
    ):

        inputs = self.preprocess_audio(
            audio_path
        )

        with torch.no_grad():

            outputs = self.model(
                **inputs
            )

            probabilities = (
                torch.softmax(
                    outputs.logits,
                    dim=1
                )[0]
            )

        predicted_id = int(
            torch.argmax(
                probabilities
            ).item()
        )

        confidence = float(
            probabilities[
                predicted_id
            ].item()
        )

        fake_probability = float(
            probabilities[0].item()
        )

        real_probability = float(
            probabilities[1].item()
        )

        return {
            "prediction": LABELS[
                predicted_id
            ],

            "confidence": confidence,

            "fake_probability":
                fake_probability,

            "real_probability":
                real_probability,
        }


if __name__ == "__main__":
    
    import sys

    classifier = ASTDeepfakeClassifier()

    if len(sys.argv) > 1:
        test_audio = Path(sys.argv[1])
    else:
        test_audio = (
            PROJECT_ROOT
            / "backend"
            / "data"
            / "processed"
            / "real_voice_real_bg_wf_2s"
            / "balanced"
            / (
                "0000__LJ038-0091__X__real_bg_0862_"
                "5bAzSNcBFxtu8sOZa9pl.wav"
            )
        )

    result = classifier.predict(
        test_audio
    )

    print("\nPrediction Result")
    print("=" * 40)

    print(
        f"Prediction: "
        f"{result['prediction']}"
    )

    print(
        f"Confidence: "
        f"{result['confidence']:.4f}"
    )

    print(
        f"Fake probability: "
        f"{result['fake_probability']:.4f}"
    )

    print(
        f"Real probability: "
        f"{result['real_probability']:.4f}"
    )