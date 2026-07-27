from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from backend.app.training.cnn_dataset import create_dataset


PROJECT_ROOT = Path(__file__).resolve().parents[3]

TRAIN_CSV = (
    PROJECT_ROOT
    / "backend"
    / "data"
    / "splits"
    / "train.csv"
)


def main():
    print(f"Reading split from: {TRAIN_CSV}")

    train_dataset = create_dataset(
        csv_path=TRAIN_CSV,
        batch_size=8,
        shuffle=True
    )

    spectrogram_batch, label_batch = next(
        iter(train_dataset)
    )

    print("\nSpectrogram batch shape:")
    print(spectrogram_batch.shape)

    print("\nLabel batch shape:")
    print(label_batch.shape)

    print("\nLabels:")
    print(label_batch.numpy())

    print("\nBatch statistics:")
    print(
        "Minimum:",
        float(np.min(spectrogram_batch.numpy()))
    )
    print(
        "Maximum:",
        float(np.max(spectrogram_batch.numpy()))
    )
    print(
        "Mean:",
        float(np.mean(spectrogram_batch.numpy()))
    )
    print(
        "Standard deviation:",
        float(np.std(spectrogram_batch.numpy()))
    )

    # Display the first Mel spectrogram
    first_spectrogram = (
        spectrogram_batch[0]
        .numpy()
        .squeeze()
    )

    plt.figure(figsize=(10, 5))

    plt.imshow(
        first_spectrogram,
        origin="lower",
        aspect="auto"
    )

    plt.xlabel("Time Frames")
    plt.ylabel("Mel Frequency Bands")
    plt.title(
        f"Normalized Mel Spectrogram - "
        f"Label: {label_batch[0].numpy()}"
    )

    plt.colorbar(label="Normalized Energy")
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()