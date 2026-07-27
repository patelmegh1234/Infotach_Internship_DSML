from pathlib import Path

import pandas as pd
import soundfile as sf
from tqdm import tqdm

from backend.app.dataset.config import (
    RAW_DATA_PATH,
    PROCESSED_DATA_PATH,
    METADATA_PATH,
)

from backend.app.preprocessing.audio_utils import (
    load_audio,
    normalize_audio,
    pad_or_trim,
)


def preprocess_dataset():

    metadata_file = METADATA_PATH / "metadata.csv"

    df = pd.read_csv(metadata_file)

    print(f"Found {len(df)} audio files")

    for _, row in tqdm(df.iterrows(), total=len(df)):

        raw_audio = RAW_DATA_PATH / row["filepath"]

        processed_audio = PROCESSED_DATA_PATH / row["filepath"]

        processed_audio.parent.mkdir(parents=True, exist_ok=True)

        try:

            audio, sr = load_audio(raw_audio)

            audio = normalize_audio(audio)

            audio = pad_or_trim(audio)

            sf.write(processed_audio, audio, sr)

        except Exception as e:

            print(f"Error processing {raw_audio}")

            print(e)

    print("\nPreprocessing Completed")


if __name__ == "__main__":

    preprocess_dataset()