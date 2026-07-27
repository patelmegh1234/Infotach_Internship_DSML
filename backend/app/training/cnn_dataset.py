from pathlib import Path

import librosa
import numpy as np
import pandas as pd
import tensorflow as tf


# --------------------------------------------------
# Audio configuration
# --------------------------------------------------

SAMPLE_RATE = 16000
DURATION = 2
NUM_SAMPLES = SAMPLE_RATE * DURATION


# --------------------------------------------------
# Mel-spectrogram configuration
# --------------------------------------------------

N_MELS = 128
N_FFT = 1024
HOP_LENGTH = 256
TARGET_FRAMES = 126


# --------------------------------------------------
# Dataset configuration
# --------------------------------------------------

BATCH_SIZE = 32
AUTOTUNE = tf.data.AUTOTUNE


# --------------------------------------------------
# Project paths
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[3]

PROCESSED_DATA_DIR = (
    PROJECT_ROOT
    / "backend"
    / "data"
    / "processed"
)


def resolve_audio_path(file_path) -> Path:
    """
    Convert the audio path stored in the CSV into an existing Path.
    """

    if isinstance(file_path, bytes):
        file_path = file_path.decode("utf-8")

    elif isinstance(file_path, np.ndarray):
        file_path = file_path.item()

        if isinstance(file_path, bytes):
            file_path = file_path.decode("utf-8")

    file_path = str(file_path).strip()

    path = Path(file_path)

    # Case 1: The path already exists
    if path.exists():
        return path

    # Case 2: The path is relative to the project root
    project_relative_path = PROJECT_ROOT / path

    if project_relative_path.exists():
        return project_relative_path

    # Case 3: The path is relative to the processed-data folder
    processed_relative_path = PROCESSED_DATA_DIR / path

    if processed_relative_path.exists():
        return processed_relative_path

    # Case 4: Search by filename inside the processed-data folder
    matching_files = list(
        PROCESSED_DATA_DIR.rglob(path.name)
    )

    if not matching_files:
        raise FileNotFoundError(
            f"Audio file not found: {file_path}"
        )

    if len(matching_files) > 1:
        print(
            f"Warning: Multiple files found for {path.name}. "
            f"Using: {matching_files[0]}"
        )

    return matching_files[0]


def load_audio(file_path) -> np.ndarray:
    """
    Load an audio file as mono audio at 16 kHz.

    Every audio sample is trimmed or padded to exactly two seconds.
    """

    resolved_path = resolve_audio_path(file_path)

    audio, _ = librosa.load(
        path=str(resolved_path),
        sr=SAMPLE_RATE,
        mono=True
    )

    audio = np.nan_to_num(
        audio,
        nan=0.0,
        posinf=0.0,
        neginf=0.0
    )

    if len(audio) > NUM_SAMPLES:
        audio = audio[:NUM_SAMPLES]

    elif len(audio) < NUM_SAMPLES:
        audio = np.pad(
            audio,
            pad_width=(0, NUM_SAMPLES - len(audio)),
            mode="constant"
        )

    return audio.astype(np.float32)


def audio_to_mel_spectrogram(
    audio: np.ndarray
) -> np.ndarray:
    """
    Convert a waveform into a normalized log-Mel spectrogram.

    Output shape:
        (128, 126, 1)
    """

    mel_spectrogram = librosa.feature.melspectrogram(
        y=audio,
        sr=SAMPLE_RATE,
        n_fft=N_FFT,
        hop_length=HOP_LENGTH,
        n_mels=N_MELS,
        power=2.0
    )

    log_mel_spectrogram = librosa.power_to_db(
        mel_spectrogram,
        ref=np.max
    )

    log_mel_spectrogram = np.nan_to_num(
        log_mel_spectrogram,
        nan=0.0,
        posinf=0.0,
        neginf=0.0
    )

    current_frames = log_mel_spectrogram.shape[1]

    if current_frames > TARGET_FRAMES:
        log_mel_spectrogram = (
            log_mel_spectrogram[:, :TARGET_FRAMES]
        )

    elif current_frames < TARGET_FRAMES:
        padding_width = TARGET_FRAMES - current_frames

        padding_value = float(
            np.min(log_mel_spectrogram)
        )

        log_mel_spectrogram = np.pad(
            log_mel_spectrogram,
            pad_width=(
                (0, 0),
                (0, padding_width)
            ),
            mode="constant",
            constant_values=padding_value
        )

    mean = np.mean(log_mel_spectrogram)
    std = np.std(log_mel_spectrogram)

    log_mel_spectrogram = (
        log_mel_spectrogram - mean
    ) / (std + 1e-8)

    log_mel_spectrogram = np.expand_dims(
        log_mel_spectrogram,
        axis=-1
    )

    return log_mel_spectrogram.astype(np.float32)


def convert_label(label) -> np.int32:
    """
    Convert string or numeric labels into binary integer labels.

    fake -> 0
    real -> 1
    """

    if isinstance(label, np.ndarray):
        label = label.item()

    if isinstance(label, bytes):
        label = label.decode("utf-8")

    if isinstance(label, str):
        label_mapping = {
            "fake": 0,
            "real": 1
        }

        normalized_label = label.strip().lower()

        if normalized_label not in label_mapping:
            raise ValueError(
                f"Unknown label: {label}. "
                "Expected 'fake', 'real', 0, or 1."
            )

        return np.int32(
            label_mapping[normalized_label]
        )

    numeric_label = int(label)

    if numeric_label not in (0, 1):
        raise ValueError(
            f"Invalid numeric label: {numeric_label}. "
            "Expected 0 or 1."
        )

    return np.int32(numeric_label)


def preprocess_audio_file(
    file_path,
    label
) -> tuple[np.ndarray, np.int32]:
    """
    Load one audio file and convert it into a CNN-ready
    Mel spectrogram.
    """

    try:
        if isinstance(file_path, bytes):
            file_path = file_path.decode("utf-8")

        elif isinstance(file_path, np.ndarray):
            file_path = file_path.item()

            if isinstance(file_path, bytes):
                file_path = file_path.decode("utf-8")

        file_path = str(file_path).strip()

        processed_label = convert_label(label)

        audio = load_audio(file_path)

        spectrogram = audio_to_mel_spectrogram(
            audio
        )

        return spectrogram, processed_label

    except Exception as error:
        print("\nCNN preprocessing failed")
        print(f"File: {file_path}")
        print(f"Label: {label}")
        print(f"Error type: {type(error).__name__}")
        print(f"Error message: {error}\n")

        raise


def create_dataset(
    csv_path: str | Path,
    batch_size: int = BATCH_SIZE,
    shuffle: bool = False
) -> tf.data.Dataset:
    """
    Create a TensorFlow dataset from a train, validation,
    or test CSV file.
    """

    csv_path = Path(csv_path)

    if not csv_path.exists():
        raise FileNotFoundError(
            f"CSV file not found: {csv_path}"
        )

    dataframe = pd.read_csv(csv_path)

    if dataframe.empty:
        raise ValueError(
            f"The CSV file is empty: {csv_path}"
        )

    possible_path_columns = [
        "file_path",
        "filepath",
        "path",
        "audio_path"
    ]

    path_column = next(
        (
            column
            for column in possible_path_columns
            if column in dataframe.columns
        ),
        None
    )

    if path_column is None:
        raise ValueError(
            "No audio-path column was found. "
            f"Available columns: "
            f"{dataframe.columns.tolist()}"
        )

    if "label" not in dataframe.columns:
        raise ValueError(
            "The CSV must contain a 'label' column."
        )

    dataframe = dataframe.dropna(
        subset=[path_column, "label"]
    ).copy()

    if dataframe.empty:
        raise ValueError(
            "No valid rows remain after removing rows "
            "with missing paths or labels."
        )

    file_paths = (
        dataframe[path_column]
        .astype(str)
        .str.strip()
        .values
    )

    labels = dataframe["label"]

    if not np.issubdtype(labels.dtype, np.number):
        label_mapping = {
            "fake": 0,
            "real": 1
        }

        normalized_labels = (
            labels
            .astype(str)
            .str.strip()
            .str.lower()
        )

        mapped_labels = normalized_labels.map(
            label_mapping
        )

        if mapped_labels.isna().any():
            unknown_labels = (
                dataframe.loc[
                    mapped_labels.isna(),
                    "label"
                ]
                .unique()
                .tolist()
            )

            raise ValueError(
                f"Unknown labels found: {unknown_labels}. "
                "Expected 'fake' or 'real'."
            )

        labels = mapped_labels.astype(
            np.int32
        ).values

    else:
        labels = labels.astype(
            np.int32
        ).values

    unique_labels = np.unique(labels)

    invalid_labels = [
        label
        for label in unique_labels
        if label not in (0, 1)
    ]

    if invalid_labels:
        raise ValueError(
            f"Invalid labels found: {invalid_labels}. "
            "Expected only 0 and 1."
        )

    dataset = tf.data.Dataset.from_tensor_slices(
        (file_paths, labels)
    )

    if shuffle:
        dataset = dataset.shuffle(
            buffer_size=len(dataframe),
            reshuffle_each_iteration=True
        )

    def tf_preprocess(
        file_path: tf.Tensor,
        label: tf.Tensor
    ):
        spectrogram, processed_label = tf.numpy_function(
            func=preprocess_audio_file,
            inp=[file_path, label],
            Tout=[tf.float32, tf.int32]
        )

        spectrogram.set_shape(
            (N_MELS, TARGET_FRAMES, 1)
        )

        processed_label.set_shape(())

        return spectrogram, processed_label

    dataset = dataset.map(
        tf_preprocess,
        num_parallel_calls=AUTOTUNE
    )

    dataset = dataset.batch(
        batch_size,
        drop_remainder=False
    )

    dataset = dataset.prefetch(AUTOTUNE)

    return dataset