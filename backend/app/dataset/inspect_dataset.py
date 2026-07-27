from pathlib import Path

import librosa
import pandas as pd

from config import RAW_DATA_PATH, METADATA_PATH


def main():

    print("=" * 60)
    print("DATASET INSPECTION")
    print("=" * 60)

    metadata = []

    corrupted = 0
    valid = 0

    for category in sorted(RAW_DATA_PATH.iterdir()):

        if not category.is_dir():
            continue

        for subtype in sorted(category.iterdir()):

            if not subtype.is_dir():
                continue

            for audio_file in sorted(subtype.glob("*.wav")):

                try:

                    audio, sr = librosa.load(audio_file, sr=None)

                    duration = librosa.get_duration(y=audio, sr=sr)

                    metadata.append({
                        "filepath": str(audio_file.relative_to(RAW_DATA_PATH)),
                        "filename": audio_file.name,
                        "category": category.name,
                        "subtype": subtype.name,
                        "sample_rate": sr,
                        "duration": round(duration, 3),
                        "status": "Valid"
                    })

                    valid += 1

                except Exception:

                    metadata.append({
                        "filepath": str(audio_file.relative_to(RAW_DATA_PATH)),
                        "filename": audio_file.name,
                        "category": category.name,
                        "subtype": subtype.name,
                        "sample_rate": None,
                        "duration": None,
                        "status": "Corrupted"
                    })

                    corrupted += 1

    df = pd.DataFrame(metadata)

    output_file = METADATA_PATH / "metadata.csv"

    df.to_csv(output_file, index=False)

    print("\nInspection Complete")
    print(f"Valid files      : {valid}")
    print(f"Corrupted files  : {corrupted}")
    print(f"\nMetadata saved to:\n{output_file}")


if __name__ == "__main__":
    main()