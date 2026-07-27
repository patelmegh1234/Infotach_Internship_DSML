from pathlib import Path

import pandas as pd
from tqdm import tqdm

from backend.app.dataset.config import (
    PROCESSED_DATA_PATH,
    METADATA_PATH,
    FEATURE_PATH,
)

from backend.app.feature_extraction.librosa_features import extract_features


def generate_feature_dataset():

    metadata_file = METADATA_PATH / "metadata.csv"

    df = pd.read_csv(metadata_file)

    extracted_features = []

    print(f"\nProcessing {len(df)} audio files...\n")

    for _, row in tqdm(df.iterrows(), total=len(df)):

        audio_path = PROCESSED_DATA_PATH / row["filepath"]

        try:

            features = extract_features(audio_path)

            # Metadata
            features["filepath"] = row["filepath"]
            features["filename"] = row["filename"]
            features["category"] = row["category"]
            features["subtype"] = row["subtype"]
            features["sample_rate"] = row["sample_rate"]
            features["duration"] = row["duration"]
            features["status"] = row["status"]

            # Binary label
            if row["category"].startswith("real_voice"):
                features["label"] = "real"
            else:
                features["label"] = "fake"

            extracted_features.append(features)

        except Exception as e:

            print(f"Error processing: {audio_path}")
            print(e)

    feature_df = pd.DataFrame(extracted_features)

    output_file = FEATURE_PATH / "features.csv"

    feature_df.to_csv(output_file, index=False)

    print("\n===================================")
    print("Feature Extraction Completed")
    print("===================================")
    print(f"Saved to: {output_file}")
    print(f"Total Samples: {len(feature_df)}")


if __name__ == "__main__":

    generate_feature_dataset()